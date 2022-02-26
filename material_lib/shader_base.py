from pathlib import Path
from typing import Optional

import bpy
import numpy as np


class Nodes:
    ShaderNodeAddShader = 'ShaderNodeAddShader'
    ShaderNodeAmbientOcclusion = 'ShaderNodeAmbientOcclusion'
    ShaderNodeAttribute = 'ShaderNodeAttribute'
    ShaderNodeBackground = 'ShaderNodeBackground'
    ShaderNodeBevel = 'ShaderNodeBevel'
    ShaderNodeBlackbody = 'ShaderNodeBlackbody'
    ShaderNodeBrightContrast = 'ShaderNodeBrightContrast'
    ShaderNodeBsdfAnisotropic = 'ShaderNodeBsdfAnisotropic'
    ShaderNodeBsdfDiffuse = 'ShaderNodeBsdfDiffuse'
    ShaderNodeBsdfGlass = 'ShaderNodeBsdfGlass'
    ShaderNodeBsdfGlossy = 'ShaderNodeBsdfGlossy'
    ShaderNodeBsdfHair = 'ShaderNodeBsdfHair'
    ShaderNodeBsdfHairPrincipled = 'ShaderNodeBsdfHairPrincipled'
    ShaderNodeBsdfPrincipled = 'ShaderNodeBsdfPrincipled'
    ShaderNodeBsdfRefraction = 'ShaderNodeBsdfRefraction'
    ShaderNodeBsdfToon = 'ShaderNodeBsdfToon'
    ShaderNodeBsdfTranslucent = 'ShaderNodeBsdfTranslucent'
    ShaderNodeBsdfTransparent = 'ShaderNodeBsdfTransparent'
    ShaderNodeBsdfVelvet = 'ShaderNodeBsdfVelvet'
    ShaderNodeBump = 'ShaderNodeBump'
    ShaderNodeCameraData = 'ShaderNodeCameraData'
    ShaderNodeClamp = 'ShaderNodeClamp'
    ShaderNodeCombineHSV = 'ShaderNodeCombineHSV'
    ShaderNodeCombineRGB = 'ShaderNodeCombineRGB'
    ShaderNodeCombineXYZ = 'ShaderNodeCombineXYZ'
    ShaderNodeCustomGroup = 'ShaderNodeCustomGroup'
    ShaderNodeDisplacement = 'ShaderNodeDisplacement'
    ShaderNodeEeveeSpecular = 'ShaderNodeEeveeSpecular'
    ShaderNodeEmission = 'ShaderNodeEmission'
    ShaderNodeFresnel = 'ShaderNodeFresnel'
    ShaderNodeGamma = 'ShaderNodeGamma'
    ShaderNodeGroup = 'ShaderNodeGroup'
    ShaderNodeHairInfo = 'ShaderNodeHairInfo'
    ShaderNodeHoldout = 'ShaderNodeHoldout'
    ShaderNodeHueSaturation = 'ShaderNodeHueSaturation'
    ShaderNodeInvert = 'ShaderNodeInvert'
    ShaderNodeLayerWeight = 'ShaderNodeLayerWeight'
    ShaderNodeLightFalloff = 'ShaderNodeLightFalloff'
    ShaderNodeLightPath = 'ShaderNodeLightPath'
    ShaderNodeMapRange = 'ShaderNodeMapRange'
    ShaderNodeMapping = 'ShaderNodeMapping'
    ShaderNodeMath = 'ShaderNodeMath'
    ShaderNodeMixRGB = 'ShaderNodeMixRGB'
    ShaderNodeMixShader = 'ShaderNodeMixShader'
    ShaderNodeNewGeometry = 'ShaderNodeNewGeometry'
    ShaderNodeNormal = 'ShaderNodeNormal'
    ShaderNodeNormalMap = 'ShaderNodeNormalMap'
    ShaderNodeObjectInfo = 'ShaderNodeObjectInfo'
    ShaderNodeOutputAOV = 'ShaderNodeOutputAOV'
    ShaderNodeOutputLight = 'ShaderNodeOutputLight'
    ShaderNodeOutputLineStyle = 'ShaderNodeOutputLineStyle'
    ShaderNodeOutputMaterial = 'ShaderNodeOutputMaterial'
    ShaderNodeOutputWorld = 'ShaderNodeOutputWorld'
    ShaderNodeParticleInfo = 'ShaderNodeParticleInfo'
    ShaderNodeRGB = 'ShaderNodeRGB'
    ShaderNodeRGBCurve = 'ShaderNodeRGBCurve'
    ShaderNodeRGBToBW = 'ShaderNodeRGBToBW'
    ShaderNodeScript = 'ShaderNodeScript'
    ShaderNodeSeparateHSV = 'ShaderNodeSeparateHSV'
    ShaderNodeSeparateRGB = 'ShaderNodeSeparateRGB'
    ShaderNodeSeparateXYZ = 'ShaderNodeSeparateXYZ'
    ShaderNodeShaderToRGB = 'ShaderNodeShaderToRGB'
    ShaderNodeSqueeze = 'ShaderNodeSqueeze'
    ShaderNodeSubsurfaceScattering = 'ShaderNodeSubsurfaceScattering'
    ShaderNodeTangent = 'ShaderNodeTangent'
    ShaderNodeTexBrick = 'ShaderNodeTexBrick'
    ShaderNodeTexChecker = 'ShaderNodeTexChecker'
    ShaderNodeTexCoord = 'ShaderNodeTexCoord'
    ShaderNodeTexEnvironment = 'ShaderNodeTexEnvironment'
    ShaderNodeTexGradient = 'ShaderNodeTexGradient'
    ShaderNodeTexIES = 'ShaderNodeTexIES'
    ShaderNodeTexImage = 'ShaderNodeTexImage'
    ShaderNodeTexMagic = 'ShaderNodeTexMagic'
    ShaderNodeTexMusgrave = 'ShaderNodeTexMusgrave'
    ShaderNodeTexNoise = 'ShaderNodeTexNoise'
    ShaderNodeTexPointDensity = 'ShaderNodeTexPointDensity'
    ShaderNodeTexSky = 'ShaderNodeTexSky'
    ShaderNodeTexVoronoi = 'ShaderNodeTexVoronoi'
    ShaderNodeTexWave = 'ShaderNodeTexWave'
    ShaderNodeTexWhiteNoise = 'ShaderNodeTexWhiteNoise'
    ShaderNodeUVAlongStroke = 'ShaderNodeUVAlongStroke'
    ShaderNodeUVMap = 'ShaderNodeUVMap'
    ShaderNodeValToRGB = 'ShaderNodeValToRGB'
    ShaderNodeValue = 'ShaderNodeValue'
    ShaderNodeVectorCurve = 'ShaderNodeVectorCurve'
    ShaderNodeVectorDisplacement = 'ShaderNodeVectorDisplacement'
    ShaderNodeVectorMath = 'ShaderNodeVectorMath'
    ShaderNodeVectorRotate = 'ShaderNodeVectorRotate'
    ShaderNodeVectorTransform = 'ShaderNodeVectorTransform'
    ShaderNodeVertexColor = 'ShaderNodeVertexColor'
    ShaderNodeVolumeAbsorption = 'ShaderNodeVolumeAbsorption'
    ShaderNodeVolumeInfo = 'ShaderNodeVolumeInfo'
    ShaderNodeVolumePrincipled = 'ShaderNodeVolumePrincipled'
    ShaderNodeVolumeScatter = 'ShaderNodeVolumeScatter'
    ShaderNodeWavelength = 'ShaderNodeWavelength'
    ShaderNodeWireframe = 'ShaderNodeWireframe'


def ensure_length(array: list, length, filler):
    if len(array) < length:
        array.extend([filler] * (length - len(array)))
        return array
    elif len(array) > length:
        return array[:length]
    return array


def create_texture(texture_path):
    return bpy.data.images.load(texture_path)


def get_missing_texture(texture_name: str, fill_color: tuple = (1.0, 1.0, 1.0, 1.0)):
    assert len(fill_color) == 4, 'Fill color should be in RGBA format'
    if bpy.data.images.get(texture_name, None):
        return bpy.data.images.get(texture_name)
    else:
        image = bpy.data.images.new(texture_name, width=512, height=512, alpha=False)
        image_data = np.full((512 * 512, 4), fill_color, np.float32).flatten()
        if bpy.app.version > (2, 83, 0):
            image.pixels.foreach_set(image_data)
        else:
            image.pixels[:] = image_data
        return image


def make_texture(texture_name, texture_dimm, texture_data, raw_texture=False):
    image = bpy.data.images.new(texture_name, width=texture_dimm[0], height=texture_dimm[1], alpha=True)
    image.alpha_mode = 'CHANNEL_PACKED'
    image.file_format = 'TARGA'
    if bpy.app.version > (2, 83, 0):
        image.pixels.foreach_set(texture_data.flatten().tolist())
    else:
        image.pixels[:] = texture_data.flatten().tolist()
    image.pack()
    if raw_texture:
        image.colorspace_settings.is_data = True
        image.colorspace_settings.name = 'Non-Color'
    return image


def clamp_value(value, min_value=0.0, max_value=1.0):
    return min(max_value, max(value, min_value))


def new_texture_name_with_suffix(old_name, suffix, ext):
    old_name = Path(old_name)
    return f'{old_name.with_name(old_name.stem)}_{suffix}.{ext}'


def clean_nodes(bpy_material):
    for node in bpy_material.node_tree.nodes:
        bpy_material.node_tree.nodes.remove(node)


def create_node(bpy_material, node_type: str, name: str = None):
    node = bpy_material.node_tree.nodes.new(node_type)
    if name:
        node.name = name
        node.label = name
    return node


def create_node_group(bpy_material, group_name, location=None, *, name=None):
    group_node = create_node(bpy_material, Nodes.ShaderNodeGroup, name or group_name)
    group_node.node_tree = bpy.data.node_groups.get(group_name)
    group_node.width = group_node.bl_width_max
    if location is not None:
        group_node.location = location
    return group_node


def create_texture_node(bpy_material, texture, name=None, location=None):
    texture_node = create_node(bpy_material, Nodes.ShaderNodeTexImage, name)
    if texture is not None:
        texture_node.image = texture
    if location is not None:
        texture_node.location = location
    return texture_node


def create_and_connect_texture_node(bpy_material, texture, color_out_target=None, alpha_out_target=None, *, name=None,
                                    uv_mode=None):
    texture_node = create_texture_node(bpy_material, texture, name)
    if color_out_target is not None:
        connect_nodes(bpy_material, texture_node.outputs['Color'], color_out_target)
    if alpha_out_target is not None:
        connect_nodes(bpy_material, texture_node.outputs['Alpha'], alpha_out_target)
    if uv_mode is not None:
        connect_nodes(bpy_material, uv_mode.outputs[0], texture_node.inputs[0])
    return texture_node


def get_node(bpy_material, name):
    return bpy_material.node_tree.nodes.get(name, None)


def connect_nodes(bpy_material, output_socket, input_socket):
    bpy_material.node_tree.links.new(output_socket, input_socket)


def insert_node(bpy_material, output_socket, middle_input_socket, middle_output_socket):
    receivers = []
    for link in output_socket.links:
        receivers.append(link.to_socket)
        bpy_material.node_tree.links.remove(link)
    connect_nodes(bpy_material, output_socket, middle_input_socket)
    for receiver in receivers:
        connect_nodes(bpy_material, middle_output_socket, receiver)


def create_nodes(material_name: str):
    bpy_material = bpy.data.materials.get(material_name, False) or bpy.data.materials.new(material_name)

    if bpy_material is None:
        raise Exception("Failed to create material")

    if bpy_material.get('ASCII_LOADED', False):
        return bpy_material

    bpy_material.use_nodes = True
    bpy_material.blend_method = 'OPAQUE'
    bpy_material.shadow_method = 'OPAQUE'
    bpy_material.use_screen_refraction = False
    bpy_material.refraction_depth = 0.2
    bpy_material['ASCII_LOADED'] = True
    return bpy_material
