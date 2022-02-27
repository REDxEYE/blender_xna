import random
from pathlib import Path

import bpy
from bpy.props import StringProperty, BoolProperty, CollectionProperty, EnumProperty, FloatProperty
import numpy as np
from mathutils import Vector, Euler, Matrix, Quaternion

from .material_lib.material_generator import generate_material
from .py_xna_lib import parse_ascii_mesh_from_file, parse_bone_names_from_file, parse_ascii_material_from_file

bl_info = {
    "name": "Blender XNA",
    "author": "RED_EYE",
    "version": (0, 0, 2),
    "blender": (3, 0, 0),
    "location": "File > Import > XNA",
    "description": "XNA models (.xna, .ascii)",
    "category": "Import-Export"
}


def get_material(mat_name, model_ob):
    md = model_ob.data
    mat = bpy.data.materials.get(mat_name, None)
    if mat:
        if md.materials.get(mat.name, None):
            for i, material in enumerate(md.materials):
                if material == mat:
                    return i
        else:
            md.materials.append(mat)
            return len(md.materials) - 1
    else:
        mat = bpy.data.materials.new(mat_name)
        mat.diffuse_color = [random.uniform(.4, 1) for _ in range(3)] + [1.0]
        md.materials.append(mat)
        return len(md.materials) - 1


class XNA_OT_ascii_import(bpy.types.Operator):
    bl_idname = "blender_xna.ascii_import"
    bl_label = "Import XNA ascii model"
    bl_options = {'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")
    files: CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)

    scale: FloatProperty(name="Scale", default=1.0, precision=6)
    filter_glob: StringProperty(default="*.ascii", options={'HIDDEN'})

    def execute(self, context):
        if Path(self.filepath).is_file():
            directory = Path(self.filepath).parent.absolute()
        else:
            directory = Path(self.filepath).absolute()

        for file in self.files:
            file = Path(directory / file.name)
            external_skeleton_path = file.with_name(file.stem + '_skel.ascii')
            remap_path = file.with_name('bonenames.txt')
            if remap_path.exists():
                print('Loading remap table')
                remap_table = parse_bone_names_from_file(remap_path.as_posix())
            else:
                remap_table = None
            if external_skeleton_available := external_skeleton_path.exists():
                skeleton = parse_ascii_mesh_from_file(external_skeleton_path.as_posix())
            else:
                skeleton = None
            model = parse_ascii_mesh_from_file(file.as_posix(), external_skeleton_available)
            bone_source = skeleton or model
            for bone in bone_source.bones:
                if remap_table is not None:
                    bone.name = remap_table.get(bone.name, bone.name)
            model_objects = []
            for mesh in model.meshes:
                mesh_name = mesh.name
                mesh_data = bpy.data.meshes.new(f'{mesh_name}_MESH')
                mesh_obj = bpy.data.objects.new(mesh_name, mesh_data)

                vertices = np.asarray(mesh.vertices, np.float32)
                vertices[:, 0], vertices[:, 1], vertices[:, 2] = (
                    vertices[:, 2].copy(), vertices[:, 0].copy(), vertices[:, 1].copy())

                mesh_data.from_pydata(vertices * self.scale, [], mesh.indices)
                mesh_data.update()
                del vertices
                mesh_data.polygons.foreach_set("use_smooth", np.ones(len(mesh_data.polygons)))
                normals = np.asarray(mesh.normals, np.float32)
                normals[:, 0], normals[:, 1], normals[:, 2] = (normals[:, 2].copy(),
                                                               normals[:, 0].copy(),
                                                               normals[:, 1].copy())
                mesh_data.normals_split_custom_set_from_vertices(normals * -1)
                mesh_data.use_auto_smooth = True
                if mesh.material:
                    amat_path = file.with_name(mesh.material.name + '.amat')
                    material = mesh.material
                    if amat_path.exists():
                        material = parse_ascii_material_from_file(amat_path.as_posix())
                    get_material(material.name, mesh_obj)
                    generate_material(material, directory)

                vertex_indices = np.zeros((len(mesh_data.loops, )), dtype=np.uint32)
                mesh_data.loops.foreach_get('vertex_index', vertex_indices)

                for uv_layer_id, uv_layer_data in mesh.uv_layers.items():
                    uv_data = mesh_data.uv_layers.new(name=f'UV_{uv_layer_id}')
                    uv_layer_data = np.array(uv_layer_data, np.float32)
                    uv_layer_data[:, 1] = 1 - uv_layer_data[:, 1]
                    uv_data.data.foreach_set('uv', uv_layer_data[vertex_indices].flatten())

                vc = mesh_data.vertex_colors.new()
                colors = np.array(mesh.vertex_colors, np.float32)
                vc.data.foreach_set('color', colors[vertex_indices].flatten())

                if external_skeleton_available or model.bones:
                    weight_groups = {bone.name: mesh_obj.vertex_groups.new(name=bone.name) for bone in
                                     bone_source.bones}

                    for n, (bone_indices, bone_weights) in enumerate(zip(mesh.bone_ids, mesh.weights)):
                        for bone_index, weight in zip(bone_indices, bone_weights):
                            if weight > 0:
                                bone_name = bone_source.bones[bone_index].name
                                weight_groups[bone_name].add([n], weight, 'REPLACE')
                else:
                    bone_ids = []
                    for bone_ids_ in mesh.bone_ids:
                        bone_ids.extend(bone_ids_)
                    bone_ids = set(bone_ids)
                    weight_groups = {str(bone): mesh_obj.vertex_groups.new(name=str(bone)) for bone in bone_ids}
                    for n, (bone_indices, bone_weights) in enumerate(zip(mesh.bone_ids, mesh.weights)):
                        for bone_index, weight in zip(bone_indices, bone_weights):
                            if weight > 0:
                                bone_name = str(bone_index)
                                weight_groups[bone_name].add([n], weight, 'REPLACE')

                bpy.context.scene.collection.objects.link(mesh_obj)
                model_objects.append(mesh_obj)

            armature = bpy.data.armatures.new(f"{file.stem}_ARM_DATA")
            armature_obj = bpy.data.objects.new(f"{file.stem}_ARM", armature)
            armature_obj.show_in_front = True
            bpy.context.scene.collection.objects.link(armature_obj)

            armature_obj.select_set(True)
            bpy.context.view_layer.objects.active = armature_obj

            bpy.ops.object.mode_set(mode='EDIT')
            bl_bones = []
            for bone in bone_source.bones:
                if remap_table is not None:
                    bone.name = remap_table.get(bone.name, bone.name)
                bl_bone = armature.edit_bones.new(bone.name[-63:])
                bl_bones.append(bl_bone)

            for bl_bone, s_bone in zip(bl_bones, bone_source.bones):
                if s_bone.parent_id != -1:
                    bl_parent = bl_bones[s_bone.parent_id]
                    bl_bone.parent = bl_parent
                bl_bone.head = (Vector(s_bone.blender_pos) * self.scale)
                bl_bone.tail = bl_bone.head + ((Vector([0, 0.05, 0]) * self.scale))
                if s_bone.quat:
                    quat = Quaternion(s_bone.blender_quat).to_matrix().to_4x4()
                    bl_bone.matrix = Matrix.Translation(s_bone.blender_pos) @ quat

            for model_obj in model_objects:
                modifier = model_obj.modifiers.new(type="ARMATURE", name="Armature")
                modifier.object = armature_obj
                model_obj.parent = armature_obj

            bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}


class XNA_MT_Menu(bpy.types.Menu):
    bl_label = "XNA models"
    bl_idname = "XNA_MT_Menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(XNA_OT_ascii_import.bl_idname, text="XNA mesh (.ascii)")
        # layout.operator(XNA_OT_ASCIIImport.bl_idname, text="XNA mesh (.xps) TODO!")


def menu_import(self, context):
    self.layout.menu(XNA_MT_Menu.bl_idname)


classes = (
    XNA_MT_Menu,
    XNA_OT_ascii_import,
)

register_, unregister_ = bpy.utils.register_classes_factory(classes)


def register():
    register_()
    bpy.types.TOPBAR_MT_file_import.append(menu_import)


def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_import)
    unregister_()
