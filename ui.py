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

import bpy
import math
import os
from collections import namedtuple

from bpy.props import (
    BoolProperty,
    IntProperty,
    FloatProperty,
    PointerProperty,   
    EnumProperty,
    StringProperty
)

from bpy.types import Panel, PropertyGroup
from . import utils


############below different.....
#properties class
def update_object(self, context):
    pass
def update_lgswrlfiles(self, context):
    pass
def my_wrl_files_callback(self, context):
    #this only applies to enum property
    items = []
    mysetuppydir = self.setupwrldir
    my_wrl_path = utils.genWRLDir(setuppydir=mysetuppydir)

    mywrlfiles = os.listdir(my_wrl_path)
    i = 0
    for file in mywrlfiles:
        myfilename = os.path.join(my_wrl_path, file)
        if os.path.isfile(myfilename) and myfilename.endswith('.wrl'):
            items.append((str(i), file.split('.wrl')[0], ""))
            i += 1
    if len(items) == 0:
        items.append(("NONE", "None", ""))
        
    return items
class LGSWrlMISCSettings(PropertyGroup):
    # FOR MISC SETTINGS
    collectionName : StringProperty(
        name = "Collection Name",
        default = ""
    )
    wrltype: EnumProperty(
        items=(
            ('1', "Structural", ""),
            ('2', "Detailer", "")),
        name="wrlType",
        description="choose wrl file by structural and detailer",
        update=update_object,
        )
    locx : FloatProperty(
        name = "fx",
        description = "translate x",
        min = -100,
        max = 100,
        default = 0.0,
        )
    locy : FloatProperty(
        name = "fy",
        description = "translate y",
        min = -100,
        max = 100,
        default = 0.0,
        )
    locz : FloatProperty(
        name = "fz",
        description = "translate z",
        min = -100,
        max = 100,
        default = 0.0,
        )

    lgswrlfiles: EnumProperty(
        items=my_wrl_files_callback,
        name="WRLs",
        description="LGS wrl files",
        update=update_lgswrlfiles,
        )
    
    setupwrldir: bpy.props.StringProperty(
        name = "Setup WRLDir",
        subtype = 'DIR_PATH',
        description = "Path to setup wrl files. Leave blank for default."
    )

    studwebwidth: EnumProperty(
        items=(
            ('1', "89", ""),
            ('2', "150", "")),
        name="Stud Width(mm)",
        description="stud web width",
        update=update_object,
        )

class FC_LGS_MISC_PT_PropsPanel(Panel):
    bl_idname = "FC_LGS_MISC_PT_PANEL"
    bl_label = "LGS"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MyLGS"
    def draw(self, context):
        settings = bpy.context.scene.lgs_misc_settings
        layout = self.layout
        
        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.resetlgsscene")

        box = layout.box()
        row = box.row()        
        col = row.column(align=True)
        col.prop(settings, 'lgswrlfiles')

        box = layout.box()
        split = box.split(factor=0.5)
        split.label(text="Setup WRLDir:")
        split.prop(settings, "setupwrldir", text="")

        row = box.row()        
        col = row.column(align=True)
        col.prop(settings, 'studwebwidth')

        row = layout.row()        
        col = row.column(align=True)
        col.operator("object.importfcdetailer", text='Import WRL')

        box = layout.box()
        row = box.row()        
        col = row.column(align=True)
        col.prop(settings, 'collectionName')

            
        row = box.row()
        col = row.column(align=True)
        col.prop(settings, 'locx')
        col = row.column(align=True)
        col.prop(settings, 'locy')
        col = row.column(align=True)
        col.prop(settings, 'locz')

        row = box.row()        
        col = row.column(align=True)
        col.operator("object.translatecol", text='Translate Collection')
        





