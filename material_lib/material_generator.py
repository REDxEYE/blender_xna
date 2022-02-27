from pathlib import Path
from ..py_xna_lib import Material
from .shader_base import *


def try_find_texture(root_path: Path, texture_name):
    try:
        for file in root_path.glob(f'{Path(texture_name).stem}.*'):
            print(file,texture_name)
            if file.suffix in ['.png', '.tga', '.dds', '.jpg', '.jpeg', '.bmp']:
                return file
    except StopIteration:
        return None


def generate_material(material: Material, root_dir: Path):
    bmat = create_nodes(material.name)
    clean_nodes(bmat)
    diffuse = create_node(bmat, Nodes.ShaderNodeBsdfDiffuse)
    gloss = create_node(bmat, Nodes.ShaderNodeBsdfGlossy)
    smix = create_node(bmat, Nodes.ShaderNodeMixShader)
    lweight = create_node(bmat, Nodes.ShaderNodeLayerWeight)
    connect_nodes(bmat, lweight.outputs[1], smix.inputs[0])
    connect_nodes(bmat, diffuse.outputs['BSDF'], smix.inputs[1])
    connect_nodes(bmat, gloss.outputs['BSDF'], smix.inputs[2])

    material_output = create_node(bmat, Nodes.ShaderNodeOutputMaterial)
    connect_nodes(bmat, smix.outputs[0], material_output.inputs['Surface'])

    if texture := material.textures.get("Diffuse"):
        texture, uv_layer = texture
        texture_path = try_find_texture(root_dir, texture)
        if texture_path is not None:
            tex_node = create_texture_node(bmat, create_texture(texture_path))
            connect_nodes(bmat, tex_node.outputs['Color'], diffuse.inputs['Color'])
    if texture := material.textures.get("Normal"):
        texture, uv_layer = texture
        texture_path = try_find_texture(root_dir, texture)
        if texture_path is not None:
            tex_node = create_texture_node(bmat, create_texture(texture_path))
            tex_node.image.colorspace_settings.is_data = True
            tex_node.image.colorspace_settings.name = 'Non-Color'
            normalmap_node = create_node(bmat, Nodes.ShaderNodeNormalMap)
            connect_nodes(bmat, tex_node.outputs['Color'], normalmap_node.inputs['Color'])

            connect_nodes(bmat, normalmap_node.outputs['Normal'], diffuse.inputs['Normal'])
            connect_nodes(bmat, normalmap_node.outputs['Normal'], gloss.inputs['Normal'])
            connect_nodes(bmat, normalmap_node.outputs['Normal'], lweight.inputs['Normal'])

    if texture := material.textures.get("Specular"):
        texture, uv_layer = texture
        texture_path = try_find_texture(root_dir, texture)
        if texture_path is not None:
            tex_node = create_texture_node(bmat, create_texture(texture_path))
            connect_nodes(bmat, tex_node.outputs['Color'], gloss.inputs['Color'])
