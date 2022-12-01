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
import gpu
import bgl
import blf
import math
import enum
import random
import os
from itertools import islice
from mathutils.bvhtree import BVHTree
from mathutils import Vector, Matrix, Euler
from gpu_extras.batch import batch_for_shader

from bpy_extras.view3d_utils import (
    region_2d_to_vector_3d,
    region_2d_to_origin_3d
)

from bpy_extras import view3d_utils
from bpy.types import Operator

import numpy as np
import bmesh
from .x3d import import_x3d
from . import ui
from . import utils
# Modal Operator
################################################################

#below different...
def translateColinCol(colname='Collection', myloc=(0, 0, 0)):
    for obj in bpy.data.collections[colname].objects:
        obj.location.x=obj.location.x + myloc[0]
        obj.location.y=obj.location.y + myloc[1]
        obj.location.z=obj.location.z + myloc[2]
    
    for col in bpy.data.collections[colname].children:
        for obj in col.objects:
            obj.location.x=obj.location.x + myloc[0]
            obj.location.y=obj.location.y + myloc[1]
            obj.location.z=obj.location.z + myloc[2]
        for subcol in col.children:
            for obj in subcol.objects:
                obj.location.x=obj.location.x + myloc[0]
                obj.location.y=obj.location.y + myloc[1]
                obj.location.z=obj.location.z + myloc[2]



class Translate_OT_Col_to_New_Location(Operator):
    bl_label = "TranslateColNewLoc"
    bl_idname = "object.translatecol"
    bl_description = "TranslateColNewLoc"
    
    @classmethod
    def poll(cls, context):
        settings = bpy.context.scene.misc_settings
        mycolname = settings.collectionName
        myselectedcol = bpy.context.view_layer.active_layer_collection
        return len(mycolname) > 0 or len(myselectedcol.name) > 0
    def execute(self, context):
        #1.挪位置
        miscsettings = bpy.context.scene.lgs_misc_settings
        myfx = miscsettings.locx
        myfy = miscsettings.locy
        myfz = miscsettings.locz
        mycolname = miscsettings.collectionName
        
        if len(mycolname) > 0:
            translateColinCol(colname=mycolname, myloc=(myfx, myfy, myfz))
        elif len(mycolname) == 0:
        
            myselectedcol = bpy.context.view_layer.active_layer_collection
            if len(myselectedcol.name) > 0:
                translateColinCol(colname=myselectedcol.name, myloc=(myfx, myfy, myfz))

        
        return {'FINISHED'}
        

class ESModalDrawOperator(Operator):
    bl_idname = "view3d.modal_operator"
    bl_label = "Simple Modal View3D Operator"
    bl_description = "Modal Operator"
    
    @classmethod
    def poll(cls, context):
        #obj = context.object
        #return obj and obj.type == "MESH"
        return True

    def modal(self, context, event):
        miscsettings = bpy.context.scene.es_misc_settings
        myobjtype = miscsettings.objtype
        myscalex = miscsettings.locx
        myscaley = miscsettings.locy
        myscalez = miscsettings.locz
        #
        if event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            if context.area.type == 'VIEW_3D':
                #Get the mouse position thanks to the event            
                self.mouse_pos = event.mouse_region_x, event.mouse_region_y
                
                region = bpy.context.region
                region3D = bpy.context.space_data.region_3d

                #Return a direction vector from the viewport at the specific 2d region coordinate.
                self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
                #Return the 3d view origin from the region relative 2d coords.
                self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
                #Return a 3d location from the region relative 2d coords, aligned with depth_location.
                self.world_loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, self.view_vector)
                print(self.world_loc, myobjtype)
                if myobjtype == '1':
                    bpy.ops.mesh.primitive_cube_add(size=1)
                    mycube=bpy.context.active_object
                    mycube.scale = (myscalex, myscaley, myscalez)
                    mycube.location = (self.world_loc[0], self.world_loc[1], 0)
                elif myobjtype == '2':
                    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=1)
                    mycylinder=bpy.context.active_object
                    mycylinder.scale = (myscalex, myscalex, myscalez)
                    mycylinder.location = (self.world_loc[0], self.world_loc[1], 0)
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            #bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            args = (self, context)
            #Add a new draw handler to this space type. It will be called every time the specified region in the space type will be drawn. Note: All arguments are positional only for now.
            #draw_type (str) – Usually POST_PIXEL for 2D drawing and POST_VIEW for 3D drawing. In some cases PRE_VIEW can be used. BACKDROP can be used for backdrops in the node editor.
            #self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}

    def execute(self, context):
        if context.area.type != 'VIEW_3D':
            print("Must use in a 3d region")
            return {'CANCELLED'}
        wm = context.window_manager
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


class Import_OT_FrameCad_Detailer_Wrl(Operator):
    bl_label = "ImportFCDetailer"
    bl_idname = "object.importfcdetailer"
    bl_description = "Import FrameCad Detailer WRL"
    
    def execute(self, context):
        #1.挪位置
        miscsettings = bpy.context.scene.lgs_misc_settings
        myfx = miscsettings.locx
        myfy = miscsettings.locy
        myfz = miscsettings.locz
        mycolname = miscsettings.collectionName
        mysetupwrldir = miscsettings.setupwrldir
        
        mywrlfileidx = int(miscsettings.lgswrlfiles)
        myitems = ui.my_wrl_files_callback(miscsettings, context)
        mywrlfilename = myitems[mywrlfileidx][1]
        
        my_wrl_path = utils.genWRLDir(setuppydir=mysetupwrldir)
        my_wrl_file_path = os.path.join(my_wrl_path, mywrlfilename + '.wrl')
        
        utils.importHSMixedFrameCadDetailor(filename=mywrlfilename, filepath=my_wrl_file_path, myloc=(myfx, myfy, myfz))
        return {'FINISHED'}

class Reset_OT_LGS_Scene(Operator):
    bl_label = "ResetScene"
    bl_idname = "object.resetlgsscene"
    bl_description = "Reset Scene"
    
    def execute(self, context):
        utils.resetScene()
        return {'FINISHED'}

