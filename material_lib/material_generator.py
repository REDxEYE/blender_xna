from pathlib import Path
from ..py_xna_lib import Material
from .shader_base import *


def try_find_texture(root_path: Path, texture_name):
    try:
        texture = next(root_path.glob(f'{texture_name}.*'))
        print(texture)
        return texture
    except StopIteration:
        return None


def generate_material(material: Material, root_dir: Path):
    bmat = create_nodes(material.name)
    clean_nodes(bmat)
    shader = create_node(bmat, Nodes.ShaderNodeBsdfPrincipled)
    material_output = create_node(bmat, Nodes.ShaderNodeOutputMaterial)
    connect_nodes(bmat, shader.outputs['BSDF'], material_output.inputs['Surface'])
    if texture := material.textures.get("Diffuse"):
        texture_path = try_find_texture(root_dir, texture)
        if texture_path is not None:
            tex_node = create_texture_node(bmat, create_texture(texture_path))
            connect_nodes(bmat, tex_node.outputs['Color'], shader.inputs['Base Color'])
    if texture := material.textures.get("Normal"):
        texture_path = try_find_texture(root_dir, texture)
        if texture_path is not None:
            tex_node = create_texture_node(bmat, create_texture(texture_path))
            normalmap_node = create_node(bmat, Nodes.ShaderNodeNormalMap)
            connect_nodes(bmat, tex_node.outputs['Color'], normalmap_node.inputs['Color'])
            connect_nodes(bmat, normalmap_node.outputs['Normal'], shader.inputs['Normal'])
