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
from . import UI
from . import Generator


bl_info = {
    "name": "Procedural building generator",
    "description": "Proceduraly generate and edit buildings",
    "author": "Luka Šimić",
    "version": (0, 8, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > PBG",
    "warning": "Under development. Might cause stability issues.",
    "wiki_url": "https://github.com/spconroy/ProceduralBuildingGenerator/wiki",
    "tracker_url": "https://github.com/spconroy/ProceduralBuildingGenerator/issues",
    "support": "COMMUNITY",
    "category": "Add Mesh"
}


def register():
    bpy.utils.register_class(UI.PBGPropertyGroup)
    bpy.types.Scene.PBGPropertyGroup = bpy.props.PointerProperty(type=UI.PBGPropertyGroup)
    bpy.utils.register_class(UI.PBG_PT_GeneralPanel)
    bpy.utils.register_class(UI.PBG_PT_LayoutPanel)
    bpy.utils.register_class(UI.PBG_PT_PillarPanel)
    bpy.utils.register_class(UI.PBG_PT_WallPanel)
    bpy.utils.register_class(UI.PBG_PT_WindowPanel)
    bpy.utils.register_class(UI.PBG_PT_WindowAbovePanel)
    bpy.utils.register_class(UI.PBG_PT_WindowUnderPanel)
    bpy.utils.register_class(UI.PBG_PT_StairsPanel)
    bpy.utils.register_class(UI.PBG_PT_RoofPanel)
    bpy.utils.register_class(UI.PBG_PT_DoorPanel)
    bpy.utils.register_class(UI.PBG_PT_GeneratePanel)
    bpy.utils.register_class(Generator.Generator)


def unregister():
    del bpy.types.Scene.PBGPropertyGroup
    bpy.utils.unregister_class(UI.PBGPropertyGroup)
    bpy.utils.unregister_class(UI.PBG_PT_GeneralPanel)
    bpy.utils.unregister_class(UI.PBG_PT_LayoutPanel)
    bpy.utils.unregister_class(UI.PBG_PT_PillarPanel)
    bpy.utils.unregister_class(UI.PBG_PT_WallPanel)
    bpy.utils.unregister_class(UI.PBG_PT_WindowPanel)
    bpy.utils.unregister_class(UI.PBG_PT_WindowAbovePanel)
    bpy.utils.unregister_class(UI.PBG_PT_WindowUnderPanel)
    bpy.utils.unregister_class(UI.PBG_PT_StairsPanel)
    bpy.utils.unregister_class(UI.PBG_PT_RoofPanel)
    bpy.utils.unregister_class(UI.PBG_PT_DoorPanel)
    bpy.utils.unregister_class(UI.PBG_PT_GeneratePanel)
    bpy.utils.unregister_class(Generator.Generator)
