# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "MyLGS",
    "author": "Derek Wang",
    "version": (1, 0, 1),
    "blender": (3, 0, 0),
    "location": "N Panel",
    "warning": "",
    "description": "for importing FrameCad wrl 3d models only",
    "doc_url": "derekwang0605@outlook.com",
    "category": "MyLGS",
}
import bpy
from . import ui
from . import operator
from bpy.props import PointerProperty
from collections import namedtuple
classes = (
    ui.LGSWrlMISCSettings,
    ui.FC_LGS_MISC_PT_PropsPanel,
    operator.Import_OT_FrameCad_Detailer_Wrl,
    operator.Translate_OT_Col_to_New_Location,
    operator.Reset_OT_LGS_Scene,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.lgs_misc_settings = PointerProperty(type=ui.LGSWrlMISCSettings)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.lgs_misc_settings
    
    