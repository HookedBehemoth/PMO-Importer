# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 22:47:34 2020

@author: AsteriskAmpersand
"""
import bpy
from mathutils import Vector, Matrix
from collections import OrderedDict
from bpy.types import Operator
MACHINE_EPSILON = 2**-8

class DummyBone():
    def __init__(self):
        self.matrix = Matrix.Identity(4)
        self.head = Vector([0,-1,0])
        self.tail = Vector([0,0,0])
        self.magnitude = 1

def createParentBone(armature):
    bone = armature.edit_bones.new("Bone.255")
    bone.head = Vector([0, 0, 0])
    bone.tail = Vector([0, MACHINE_EPSILON, 0])
    bone.matrix = Matrix.Identity(4)        
    return bone

def createBone(armature, obj, parent_bone = None):
    bone = armature.edit_bones.new(obj.name)
    bone.head = Vector([0, 0, 0])
    bone.tail = Vector([0, MACHINE_EPSILON, 0])#Vector([0, 1, 0])
    if not parent_bone:
        parent_bone = DummyBone()#matrix = Identity(4), #boneTail = 0,0,0, boneHead = 0,1,0
    bone.matrix = parent_bone.matrix * obj.matrix_local
    for child in obj.children:
        nbone = createBone(armature, child, bone)
        nbone.parent = bone
    if "id" in obj: bone["id"] = obj["id"]
    return bone

def createArmature(rootBone):#Skeleton
    bpy.ops.object.select_all(action='DESELECT')
    blenderArmature = bpy.data.armatures.new('Armature')
    arm_ob = bpy.data.objects.new('Armature', blenderArmature)
    bpy.context.scene.collection.objects.link(arm_ob)
    bpy.context.view_layer.update()
    arm_ob.select_set(True)
    arm_ob.show_in_front = True
    bpy.context.view_layer.objects.active = arm_ob
    arm_ob.data.display_type = 'STICK'
    bpy.ops.object.mode_set(mode='EDIT')    
    empty = createParentBone(blenderArmature)
    
    root = createBone(blenderArmature, rootBone)
    root.parent = empty
        #arm.pose.bones[ix].matrix        
    bpy.ops.object.editmode_toggle()
    for obj in bpy.context.scene.collection.objects:
        if obj.type == "MESH":
            m = obj.modifiers.new("Armature","ARMATURE")
            m.object = arm_ob
    return

class ConvertAHI(Operator):
    bl_idname = "fu_tools.convert_ahi"
    bl_label = "Convert AHI to Armature"
    bl_options = {'REGISTER', 'PRESET', 'UNDO'}
    
    def execute(self,context):
        roots = [ o for o in bpy.context.scene.collection.objects if o.type == "EMPTY" and o.parent is None ]
        for root in roots: createArmature(root)
        return {'FINISHED'}