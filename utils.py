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
import os
import bmesh
from mathutils import Vector, Matrix, Euler
import numpy as np
import bmesh
from .x3d import import_x3d

def genWRLDir(setuppydir=''):
    if os.path.isdir(setuppydir) == True:
        return setuppydir
    #dir_path = os.path.dirname(os.path.dirname(__file__))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    sub_path = r'wrls'
    my_wrl_path = os.path.join(dir_path, sub_path)
    return my_wrl_path

#Recursivly transverse layer_collection for a particular name
def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

def genStud(myparalen = 1000):
    bm = bmesh.new()
    mypointlist = [(41.000,0, 0),(0,0,0),(0,0,-89.000), (41.000,0,-89.000),(41.000,0,-78.000), (40.000,0,-78.000), (40.000,0,-88.000), (1,0,-88.000),(1,0,-1), (40.000,0,-1), (40.000,0,-11.000), (41.000,0,-11.000), (41.000,0,0)]
    mypointlist = [(41.000,0, 0),(0,0,0),(0,0,-89.000), (41.000,0,-89.000),(41.000,0,-44.500), (40.000,0,-44.500), (40.000,0,-88.000), (1,0,-88.000),(1,0,-1), (40.000,0,-1), (40.000,0,-44.500), (41.000,0,-44.500), (41.000,0,0)]
    pointlist = [(i[0]/myparalen, i[1]/myparalen, i[2]/myparalen) for i in mypointlist]
    
    for mypoint in pointlist:
        bm.verts.new(mypoint)
    bverts=bm.verts[:]
    facelist=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    i = 0
    fllen = len(facelist)
    for i, fi in enumerate(facelist):
        if i < fllen - 1:
            bm.edges.new((bverts[i], bverts[i+1]))
        
    
    edges_start_a = bm.edges[:]
    ret = bmesh.ops.extrude_edge_only(bm,edges=edges_start_a)
    geom_extrude_mid = ret["geom"]
    del ret
    verts_extrude_b = [ele for ele in geom_extrude_mid if isinstance(ele, bmesh.types.BMVert)]
    
    bmesh.ops.translate(
        bm,
        verts=verts_extrude_b,
        vec=(0.0, 1 / myparalen, 0))    
    my1stprofile=bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.solidify(bm, geom=my1stprofile, thickness=2 / myparalen)   
    
    me = bpy.data.meshes.new("Mesh")
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new("cshape", me)
    bpy.context.collection.objects.link(obj)
    return obj

def genVGMat01(obj,color_A=(0,0,0),prefix='Random',color_B=(1,1,1),hue=0.5,hue_variation=0.6,seed=0,count=3,generate_materials=False,random_colors=True):
    #copy from Tissue
    try: obj.name
    except: return None
    
    if len(obj.material_slots) == 0:
        generate_materials = True
        if generate_materials:
            colA = Vector(color_A)
            colB = Vector(color_B)
            h1 = (hue - hue_variation/2)
            h2 = (hue + hue_variation/2)
            #count = self.count
            obj.data.materials.clear()
            materials = []
            for i in range(count):
                mat_name = '{}{:03d}'.format(prefix,i)
                mat = bpy.data.materials.new(mat_name)
                if random_colors:
                    mat.diffuse_color = colorsys.hsv_to_rgb((h1 + (h2-h1)/(count)*i)%1, 1, 1)[:] + (1,)
                else:
                    CV=(colA + (colB - colA)/(count-1)*i)
                    mat.diffuse_color = (CV[0],CV[1],CV[2],1)
                obj.data.materials.append(mat)
                
            else:
                count = len(obj.material_slots)
            np.random.seed(seed=seed)
            n_faces = len(obj.data.polygons)
            if count > 0:
                rand = list(np.random.randint(count, size=n_faces))
                obj.data.polygons.foreach_set('material_index',rand)
                obj.data.update()

def genDiffuseMat01(obj,diffusecolor=(0,0,0)):
    try: obj.name
    except: return None
    
    if len(obj.material_slots) == 0:
        obj.data.materials.clear()
        mat_name = '{}{:03d}'.format('dc',1)
        mat = bpy.data.materials.new(mat_name)
        mat.diffuse_color = (diffusecolor[0],diffusecolor[1],diffusecolor[2],1)
        obj.data.materials.append(mat)


def resetScene():

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_post.clear()
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    C = bpy.context
    node_tree = C.scene.node_tree
    if node_tree is not None:
        for node in node_tree.nodes:
            node_tree.nodes.remove(node)

    for key in bpy.data.node_groups:
        bpy.data.node_groups.remove(key)
    for tex in bpy.data.textures:
        bpy.data.textures.remove(tex)
    for mat in bpy.data.materials:
        bpy.data.materials.remove(mat)
    #for background nodes
    for key in bpy.data.worlds['World'].node_tree.nodes:
        bpy.data.worlds['World'].node_tree.nodes.remove(key)
    bpy.context.scene.world.use_nodes=False
    bpy.context.scene.world.color=(0,0,0)
    for mycollection in bpy.data.collections:
        if mycollection.name!='Collection':
            bpy.data.collections.remove(mycollection)


def importHSMixedFrameCadDetailor(filename='', filepath='', myloc=(0, 0, 0)):
    bpy.ops.object.select_all(action='DESELECT')
    
    myparalen = 1000
    bpycollection = bpy.context.collection
    global_matrix = None
    if global_matrix is None:
        global_matrix = Matrix()
    context = bpy.context
    scene = context.scene
    root_node,msg = import_x3d.vrml_parse(filepath)
    all_nodes = root_node.getSerialized([], [])
    
    diffusecolor = (0, 0.5, 0, 1)
                
    sca = []
    mycollections = []
    listcolordicts = {}
    
    obj = genStud()
    mesh = obj.data
    
    my_total_coll = bpy.data.collections.new(filename)
    bpy.context.scene.collection.children.link(my_total_coll)
    
    
     
    
    my_villa_coll = bpy.data.collections.new(filename + "_Villa Collection")
    my_total_coll.children.link(my_villa_coll)

    my_hs_coll = bpy.data.collections.new(filename + "_HS Collection")
    my_villa_coll.children.link(my_hs_coll)
    
    
    villalayer_collection = bpy.context.view_layer.layer_collection
    villalayerColl = recurLayerCollection(villalayer_collection, filename + "_Villa Collection")
    bpy.context.view_layer.active_layer_collection = villalayerColl
    
    mywildcard = '.'
    i = 0
    #translate in transform
    itt = 0
    tfdef = ''
    mytfdefp1 = ''
    for node, ancestry in all_nodes:
         
        
        spec = node.getSpec()
        if spec == 'Transform':
            cent = node.getFieldAsFloatTuple('center', None, ancestry)  # (0.0, 0.0, 0.0)
            rot = node.getFieldAsFloatTuple('rotation', None, ancestry)  # (0.0, 0.0, 1.0, 0.0)
            sca = node.getFieldAsFloatTuple('scale', None, ancestry)  # (1.0, 1.0, 1.0)
            scaori = node.getFieldAsFloatTuple('scaleOrientation', None, ancestry)  # (0.0, 0.0, 1.0, 0.0)
            tx = node.getFieldAsFloatTuple('translation', None, ancestry)  # (0.0, 0.0, 0.0)
            
            if itt == 0:
                mytranslation = node.fields[0]
                myloc = Vector((float(mytranslation[1]), float(mytranslation[2]), float(mytranslation[3]))) / myparalen
            if len(node.id) == 3 and node.id[2] == 'Transform':
                tfdef = filename +'_' + node.getDefName()
                mytfdefp1 = tfdef
                
                
                mycollections.append(tfdef)
                #adding collection here
                my_wall_coll = bpy.data.collections.new(tfdef)
                my_villa_coll.children.link(my_wall_coll)
                layer_collection = bpy.context.view_layer.layer_collection
                layerColl = recurLayerCollection(layer_collection, tfdef)
                bpy.context.view_layer.active_layer_collection = layerColl
                
            itt+=1  

        elif spec=='Material':

            if node.fields[0][0] == 'diffuseColor':   
                diffusecolor = (float(node.fields[0][1]), float(node.fields[0][2]), float(node.fields[0][3]), 1) 
            elif node.fields[1][0] == 'diffuseColor':   
                diffusecolor = (float(node.fields[1][1]), float(node.fields[1][2]), float(node.fields[1][3]), 1) 
            
        elif spec == 'Extrusion':   
            etdef=node.getDefName()
            if etdef=='Ground_Reference' or etdef=='"VRML_Object"':
                   
                #heavy section
                self_real = node.getRealNode()
            
                geom = node.children[0]
                geom_spec = geom.getSpec()
                
                newarray_data = [i for i in geom.array_data if(len(i)!=0)]
                
                for myarray in newarray_data:
                    if len(myarray) == 2:
                        pointlist.append((myarray[0] / myparalen, 0, myarray[1] / myparalen))
                            
                myspine=node.children[1]
                spinearray_data = [i for i in myspine.array_data if(len(i)!=0)]
                if etdef=='Ground_Reference':
                    sy1=spinearray_data[0][1] * -1
                    sy2=spinearray_data[1][1] * -1
                    sygap=sy1-sy2
                elif etdef=='"VRML_Object"':
                    sy1=spinearray_data[0][1] * -1
                    sy2=spinearray_data[1][1] * -1
                    sygap=sy2-sy1
                try:
                    villahslayer_collection = bpy.context.view_layer.layer_collection
                    villahslayerColl = recurLayerCollection(villahslayer_collection, filename + "_HS Collection")
                    bpy.context.view_layer.active_layer_collection = villahslayerColl

                    facelist=[(0,1,2,3,4)]
        
                    mesh_data = bpy.data.meshes.new("cube_mesh_data")
                    mesh_data.from_pydata(pointlist, [], facelist)
                    mesh_data.update()

                    
                    hsobj = bpy.data.objects.new(filename + "_HS", mesh_data)
                    bpy.context.collection.objects.link(hsobj)
                    bpy.context.view_layer.objects.active = hsobj
                    #hsobj.name = filename
                    hsobj.select_set(True)
                    bpy.ops.object.modifier_add(type='SOLIDIFY')
                    bpy.context.object.modifiers["Solidify"].thickness = sygap / myparalen
                    
                    hsobj.location.y = hsobj.location.y - sy1/myparalen
                    #hsobj.location.x = hsobj.location.x - myloc[0]
                    #hsobj.location.y = hsobj.location.y - myloc[1]
                    #hsobj.location.z = hsobj.location.z - myloc[2]
                    
                    
                    if etdef == 'Ground_Reference':
                        myhue=0.43966
                        
                    elif etdef == '"VRML_Object"':
                        myhue=0.966
                         
                    genDiffuseMat01(hsobj,diffusecolor=diffusecolor)

                             
                except Exception as e:
                    print (str(e))
            else:
                fm = import_x3d.getFinalMatrix(node, None, ancestry, global_matrix)
                fm[0][3] = fm[0][3] / myparalen
                fm[1][3] = fm[1][3] / myparalen
                fm[2][3] = fm[2][3] / myparalen
                
                try:
                    if (np.round(abs(fm.to_euler().y),2) % 1.57==0 and np.round(abs(fm.to_euler().z),2) % 1.57==0) or ((np.round(abs(fm.to_euler().y),2) % 1.57!=0 or np.round(abs(fm.to_euler().z),2) % 1.57!=0) and etdef[:2]!='Br' and etdef[:1]!='W'  and etdef[:2]!='Kb'   and etdef[:1]!='B'):
                        mynewobjName = filename + mywildcard + tfdef + mywildcard + etdef + mywildcard + str(i)
                        mynewobj = bpy.data.objects.new(mynewobjName, mesh.copy())
                        
                        bpy.context.collection.objects.link(mynewobj)                   
                        mynewobj.matrix_world = fm
                        mynewobj.rotation_euler = fm.to_euler()
                        mynewobj.scale.y = fm.to_scale()[1]
                        #used for generating integrated effects
 
                        mynewobj.location.x = mynewobj.location.x - myloc[0]
                        mynewobj.location.y = mynewobj.location.y - myloc[1]
                        mynewobj.location.z = mynewobj.location.z - myloc[2]
                        
                        #TAKE TOO LONG,SELECT ALL THEN SET ORIGIN AT ONCE
                        if len(tfdef)>0 :
                            listcolordicts[tfdef] = diffusecolor
                        genDiffuseMat01(mynewobj,diffusecolor=diffusecolor)
                        #myhue=0.66
                        #genVGMat01(mynewobj,color_A=(random(),0.3,0),prefix='Random',color_B=(1,random(),random()),hue=myhue,hue_variation=myhue+0.1,seed=0,count=3,generate_materials=False,random_colors=True)  
                        
                    
                except Exception as e:
                    print (str(e))
                    

        pointlist = []
        i+=1
    
    bpy.data.objects.remove(obj, do_unlink = True)
    
    for obj in bpy.data.collections[filename + "_HS Collection"].objects:
        pass
        obj.location.x  = obj.location.x - myloc[0]
        obj.location.y = obj.location.y - myloc[1]
        obj.location.z = obj.location.z - myloc[2]

    
    
    #bpy.context.view_layer.active_layer_collection = villalayerColl
    #bpy.ops.object.select_all(action='SELECT')
    selectAllObjsinCol(colname=filename)
    bpy.ops.transform.rotate(value=3.14/2, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0.0, 0.0), (0.0, 1, 0.0), (0.0, 0.0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1.0, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_target='CLOSEST', snap_point=(0.0, 0.0, 0.0), snap_align=False, snap_normal=(0.0, 0.0, 0.0), gpencil_strokes=False, center_override=(0.0, 0.0, 0.0), release_confirm=False, use_accurate=False)
    
def selectAllObjsinCol(colname='Collection'):
    for obj in bpy.data.collections[colname].objects:
        obj.select_set(True)
        
    for col in bpy.data.collections[colname].children:
        for obj in col.objects:
            obj.select_set(True)
            
        for subcol in col.children:
            for obj in subcol.objects:
                obj.select_set(True)
                