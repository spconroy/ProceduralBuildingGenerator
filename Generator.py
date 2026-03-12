# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Procedural building generator
#  Copyright (C) 2019 Luka Simic
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from . import GenLayout
from . import GenMesh
from . import GenUtils
import time
import os


class Generator(bpy.types.Operator):
    # TODO: docstring

    bl_idname = "pbg.generate_building"
    bl_label = "Generate Building"

    def execute(self, context):
        collection = bpy.data.collections.get("pbg_collection")
        if not collection:
            collection = bpy.data.collections.new("pbg_collection")
            bpy.context.scene.collection.children.link(collection)
        else:
            # delete all objects from collection
            for obj in list(collection.objects):
                bpy.data.objects.remove(obj, do_unlink=True)

        # generate stuff needed for other functions that generate geometry
        time_start = time.time()
        params_general = GenLayout.ParamsGeneral.from_ui()
        params_section = GenUtils.ParamsSectionFactory.horizontal_separator_params_large()
        params_pillar = GenMesh.ParamsPillar.from_ui()
        params_walls = GenMesh.ParamsWalls.from_ui()
        params_windows_under = GenMesh.ParamsWindowsUnder.from_ui()
        params_windows_above = GenMesh.ParamsWindowsAbove.from_ui()
        params_footprint = GenLayout.ParamsFootprint.from_ui()
        params_stairs = GenMesh.ParamsStairs.from_ui()
        params_windows = GenMesh.ParamsWindows.from_ui()
        params_roof = GenMesh.ParamsRoof.from_ui()
        params_door = GenMesh.ParamsDoor.from_ui()

        door_position = ((0.0, 0.5*params_footprint.building_depth+params_footprint.building_wedge_depth,
                          params_general.floor_offset), 0)
        door_positions = list()
        # TODO: fix this door position mess, not sure if the zero above is critical
        door_positions.append((door_position[0], door_position[1], params_general.floor_offset))

        footprint = GenLayout.gen_footprint(params_footprint)
        layout = GenLayout.gen_layout(params_general, footprint, door_position)
        section_element_list = GenUtils.gen_section_element_list(params_section)
        section_mesh = GenUtils.gen_section_mesh(section_element_list, params_general.separator_height,
                                                 params_general.separator_width)
        if params_general.generate_separator == True:
            wall_section_height = params_general.floor_height - params_general.separator_height
        else:
            wall_section_height = params_general.floor_height
        # end if
        wall_section_mesh = GenUtils.gen_wall_section_mesh(params_walls.type, wall_section_height,
                                                           params_walls.section_size,
                                                           params_walls.mortar_size,
                                                           params_walls.row_count)

        # generate geometry
        obj_separator = None
        if params_general.generate_separator == True:
            obj_separator = GenMesh.gen_mesh_floor_separator(context, footprint, section_mesh.copy())
            collection.objects.link(obj_separator)
            separator_positions = list()
            for i in range(0, params_general.floor_count+1):
                separator_positions.append(((0, 0, params_general.floor_offset + wall_section_height +
                                            i*params_general.floor_height), 0))
            apply_positions(obj_separator, separator_positions, collection)
            obj_separator.hide_set(True)
        # end if
        obj_wall = GenMesh.gen_mesh_wall(context, layout["wall_loops"], wall_section_mesh.copy())
        collection.objects.link(obj_wall)
        obj_offset_wall = GenMesh.gen_mesh_offset_wall(context, footprint, params_general, params_walls)
        collection.objects.link(obj_offset_wall)
        obj_stairs = GenMesh.gen_mesh_stairs(context, params_general, params_footprint, params_stairs)
        collection.objects.link(obj_stairs)

        obj_window_under = GenMesh.gen_mesh_windows_under(context, params_general, params_windows_under, wall_section_mesh)
        collection.objects.link(obj_window_under)
        apply_positions(obj_window_under, layout["window_positions"], collection)
        obj_window_under.hide_set(True)

        obj_window_above = GenMesh.gen_mesh_windows_above(context, params_general, params_windows_above, wall_section_mesh)
        collection.objects.link(obj_window_above)
        apply_positions(obj_window_above, layout["window_positions"], collection)
        obj_window_above.hide_set(True)

        obj_window_around = GenMesh.gen_mesh_windows_around(context, params_general, params_windows)
        collection.objects.link(obj_window_around)
        apply_positions(obj_window_around, layout["window_positions"], collection)
        obj_window_around.hide_set(True)

        obj_window = GenMesh.gen_mesh_windows(context, params_general, params_windows)
        collection.objects.link(obj_window)
        apply_positions(obj_window, layout["window_positions"], collection)
        obj_window.hide_set(True)

        obj_door_above = GenMesh.gen_mesh_door_above(context, params_general, wall_section_mesh)
        collection.objects.link(obj_door_above)
        apply_positions(obj_door_above, door_positions, collection)
        obj_door_above.hide_set(True)

        obj_door_around = GenMesh.gen_mesh_door_around(context, params_general, params_door)
        collection.objects.link(obj_door_around)
        apply_positions(obj_door_around, door_positions, collection)
        obj_door_around.hide_set(True)

        obj_door = GenMesh.gen_mesh_door(context, params_general, params_door)
        collection.objects.link(obj_door)
        apply_positions(obj_door, door_positions, collection)
        obj_door.hide_set(True)

        obj_pillar = None
        if params_general.generate_pillar == True:
            obj_pillar = GenMesh.gen_mesh_pillar(context, params_pillar, params_general, section_mesh.copy())
            collection.objects.link(obj_pillar)
            apply_positions(obj_pillar, layout["pillar_positions"], collection)
            obj_pillar.hide_set(True)
        # end if

        obj_roof = GenMesh.gen_mesh_roof(context, params_general, footprint, params_footprint, params_roof)
        collection.objects.link(obj_roof)

        time_end = time.time()
        msg = "generation finished in " + str(time_end - time_start) + " seconds"
        print(msg)

        time_start = time.time()
        material_dict = load_materials()
        time_end = time.time()
        msg = "loading materials finished in " + str(time_end - time_start) + " seconds"

        # apply materials to objects
        time_start = time.time()
        if obj_separator:
            obj_separator.data.materials.append(material_dict["pbg_color2"])
        obj_wall.data.materials.append(material_dict["pbg_color1"])
        obj_offset_wall.data.materials.append(material_dict["pbg_color2"])
        obj_stairs.data.materials.append(material_dict["pbg_color2"])
        obj_window_around.data.materials.append(material_dict["pbg_color2"])
        obj_door_above.data.materials.append(material_dict["pbg_color1"])
        obj_door_around.data.materials.append(material_dict["pbg_color2"])
        obj_door.data.materials.append(material_dict["pbg_wood"])
        obj_roof.data.materials.append(material_dict["pbg_roof"])
        if obj_pillar:
            obj_pillar.data.materials.append(material_dict["pbg_color2"])
        # TODO:
        if params_windows_under.type == "WALL" or params_windows_under.type == "PILLARS":
            obj_window_under.data.materials.append(material_dict["pbg_color1"])
        else:
            obj_window_under.data.materials.append(material_dict["pbg_color2"])
        if params_windows_above.type == "WALL":
            obj_window_above.data.materials.append(material_dict["pbg_color1"])
        else:
            obj_window_above.data.materials.append(material_dict["pbg_color2"])
        obj_window.data.materials.append(material_dict["pbg_wood"])
        obj_window.data.materials.append(material_dict["pbg_glass"])
        time_end = time.time()
        msg = "applying materials finished in " + str(time_end - time_start) + " seconds"
        print(msg)
        return {"FINISHED"}
    # end invoke
# end Generator


def apply_positions(obj: bpy.types.Object, positions: list, collection):
    """
        Duplicates (linked duplicate) the given object onto the given positions
        applies the given rotation
    Args:
        collection: collection where to keep the object
        obj: object to duplicate, origin should be in (0, 0, 0)
        positions: list(tuple(tuple(x,y,z), rot)) - object positions and rotations
    Returns:

    """
    for position in positions:
        dup = obj.copy()
        collection.objects.link(dup)
        # move it
        dup.location.x = position[0][0]
        dup.location.y = position[0][1]
        dup.location.z = position[0][2]
        # rotate it
        dup.rotation_euler.z = position[1]
# end apply_positions


def _get_texture_cache_dir():
    """Get or create the texture cache directory next to this addon."""
    cache_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "textures_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def _download_polyhaven_texture(texture_id, map_type, resolution="1k"):
    """
    Download a Poly Haven texture map if not already cached.
    Returns the local file path.
    """
    import urllib.request
    cache_dir = _get_texture_cache_dir()
    filename = f"{texture_id}_{map_type}_{resolution}.jpg"
    filepath = os.path.join(cache_dir, filename)

    if os.path.exists(filepath):
        return filepath

    url = f"https://dl.polyhaven.org/file/ph-assets/Textures/jpg/{resolution}/{texture_id}/{filename}"
    print(f"    Downloading: {url}")
    try:
        urllib.request.urlretrieve(url, filepath)
        return filepath
    except Exception as e:
        print(f"    WARNING: Failed to download {url}: {e}")
        return None


def _create_pbr_material(name, texture_id, tint=None):
    """
    Create a Principled BSDF material with Poly Haven PBR textures.
    Downloads diffuse, normal, and roughness maps.
    Optional tint multiplies the diffuse color.
    """
    mat = bpy.data.materials.get(name)
    if mat:
        return mat

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")

    # Download texture maps
    diff_path = _download_polyhaven_texture(texture_id, "diff")
    nor_path = _download_polyhaven_texture(texture_id, "nor_gl")
    rough_path = _download_polyhaven_texture(texture_id, "rough")

    x_offset = -600

    # Diffuse / Base Color
    if diff_path:
        tex_diff = nodes.new("ShaderNodeTexImage")
        tex_diff.location = (x_offset, 300)
        tex_diff.image = bpy.data.images.load(diff_path)
        tex_diff.image.colorspace_settings.name = 'sRGB'
        if tint:
            mix = nodes.new("ShaderNodeMix")
            mix.data_type = 'RGBA'
            mix.location = (x_offset + 300, 300)
            mix.inputs[0].default_value = 1.0  # factor
            mix.blend_type = 'MULTIPLY'
            mix.inputs[6].default_value = tint  # Color B
            links.new(tex_diff.outputs["Color"], mix.inputs[7])  # Color A (index 7 for RGBA)
            links.new(mix.outputs[2], bsdf.inputs["Base Color"])  # Result (index 2 for RGBA)
        else:
            links.new(tex_diff.outputs["Color"], bsdf.inputs["Base Color"])

    # Normal map
    if nor_path:
        tex_nor = nodes.new("ShaderNodeTexImage")
        tex_nor.location = (x_offset, -100)
        tex_nor.image = bpy.data.images.load(nor_path)
        tex_nor.image.colorspace_settings.name = 'Non-Color'
        normal_map = nodes.new("ShaderNodeNormalMap")
        normal_map.location = (x_offset + 300, -100)
        links.new(tex_nor.outputs["Color"], normal_map.inputs["Color"])
        links.new(normal_map.outputs["Normal"], bsdf.inputs["Normal"])

    # Roughness map
    if rough_path:
        tex_rough = nodes.new("ShaderNodeTexImage")
        tex_rough.location = (x_offset, -400)
        tex_rough.image = bpy.data.images.load(rough_path)
        tex_rough.image.colorspace_settings.name = 'Non-Color'
        links.new(tex_rough.outputs["Color"], bsdf.inputs["Roughness"])

    return mat


def _create_simple_material(name, color, roughness=0.8, metallic=0.0, alpha=1.0):
    """Fallback: create a solid-color Principled BSDF material."""
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    if alpha < 1.0:
        mat.blend_method = 'BLEND'
        if bsdf:
            bsdf.inputs["Alpha"].default_value = alpha
    return mat


def load_materials() -> dict:
    """
    Create Principled BSDF materials with Poly Haven PBR textures.
    Materials: pbg_wood, pbg_glass, pbg_color1, pbg_color2, pbg_roof
    Falls back to solid colors if texture download fails.
    """
    print("  Loading Poly Haven PBR materials...")
    materials = {
        # Wall primary — plastered wall texture
        "pbg_color1": _create_pbr_material(
            "pbg_color1", "plastered_wall"),
        # Wall accent / trim — worn plaster
        "pbg_color2": _create_pbr_material(
            "pbg_color2", "worn_plaster_wall"),
        # Wood — weathered planks for doors and window frames
        "pbg_wood": _create_pbr_material(
            "pbg_wood", "weathered_planks"),
        # Glass — simple semi-transparent material (no texture needed)
        "pbg_glass": _create_simple_material(
            "pbg_glass", (0.15, 0.18, 0.25, 1.0), roughness=0.1, metallic=0.1, alpha=0.6),
        # Roof — clay roof tiles
        "pbg_roof": _create_pbr_material(
            "pbg_roof", "clay_roof_tiles_02"),
    }
    return materials
