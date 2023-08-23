bl_info = {
    "name" : "SyncRenderSets",
    "author" : "CP-Design", 
    "description" : "Unified management to synchronize all scene rendering settings and passes for all view layers",
    "blender" : (3, 0, 0),
    "version" : (1, 0, 1),
    "location" : "3Dview > Nplane > SyncRenderSets",
    "doc_url": "https://github.com/chenpaner", 
    "tracker_url": "", 
    "category" : "CP" 
}

import bpy

class COLORMAN_PT_Panel(bpy.types.Panel):#色彩管理
    bl_idname = "COLORMAN_PT_Panel"
    bl_label = "Color Management"#色彩管理
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SyncRenderSets'
    bl_order = 4  # 面板的显示顺序
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def draw(self, context):
        layout = self.layout
        scenes = bpy.data.scenes
        
        for scene in scenes:
            row = layout.row(align=True)
            col_label = row.column()
            col_label.scale_x = 2.0#

            scene_icon = "SCENE_DATA"  # 默认图标
            scene_txt = ""  # 默认文字
            if scene.name == bpy.context.scene.name:
                scene_icon = "FUND"  # 当前场景的图标
                scene_txt = "【Current】"
                col_label.alert = True
            col_label.label(text= f" {scene.name}" + scene_txt, icon=scene_icon)  # 场景名称

            col_prop = row.column()
            col_prop.prop(scene.view_settings, "use_curve_mapping", text="Use Curves") 
            
            render_box = layout.box()
            column = render_box.column_flow(columns=1)#分为两列进行布局,无法手动设置列数
            column.prop(scene.display_settings, "display_device", text="Display Device")
            column.prop(scene.view_settings, "view_transform", text="View Transform")
            column.prop(scene.view_settings, "look", text="Look")
               
            column2 = render_box.column_flow(columns=2 ,align=True)#分为两列进行布局,无法手动设置列数
            column2.prop(scene.view_settings, "exposure")
            column2 .prop(scene.view_settings, "gamma")

            
            layout.separator()
            
class LIGHTPATHS_PT_Panel(bpy.types.Panel):#光程
    bl_idname = "LIGHTPATHS_PT_Panel"
    bl_label = "Light Paths"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SyncRenderSets'
    bl_order = 3  # 面板的显示顺序
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def draw(self, context):
        layout = self.layout
        scenes = bpy.data.scenes
        
        for scene in scenes:
            row = layout.row(align=True)
            col_label = row.column()
            col_label.scale_x = 1.5#
            scene_icon = "SCENE_DATA"  # 默认图标
            scene_txt = ""  # 默认文字
            if scene.name == bpy.context.scene.name:
                scene_icon = "FUND"  # 当前场景的图标
                scene_txt = "【Current】"
                col_label.alert = True
            col_label.label(text= f" {scene.name}" + scene_txt, icon=scene_icon)  # 场景名称
            col0_prop = row.column()
            col0_prop.operator("scene.sync_light_paths", text="Sync", icon="UV_SYNC_SELECT").scene_index = scenes.find(scene.name)

            renderset_box = layout.box()#整体box
        # 光程面板
            if scene.render.engine == 'CYCLES':
                ligthpaths_box = renderset_box.column()
                row = ligthpaths_box.row(align=True)
                #row.scale_y = 1.5 # 缩小行的高度
                col_label = row.column()
                col_label.scale_x = 1.0#
                col_label.label(text='Light Paths')#光程
                col_prop = row.column()           
                col_prop.prop(scene.cycles, "max_bounces", text="Total")
               
                row = ligthpaths_box.row(heading='', align=True)
                row.prop(scene.cycles, "diffuse_bounces", text="Diffuse")
                row.prop(scene.cycles, "glossy_bounces", text="Glossy")
                row.prop(scene.cycles, "transmission_bounces", text="Transmission")
                row.prop(scene.cycles, "volume_bounces", text="Volume")
                row.prop(scene.cycles, "transparent_max_bounces", text="Transparent")
                
                row = ligthpaths_box.row(heading='', align=True)
                row.prop(scene.cycles, "caustics_reflective", text="Refractive")#焦散反射
                row.prop(scene.cycles, "caustics_refractive", text="Refractive")#焦散折射

                row.prop(scene.cycles, "use_fast_gi", text="Fast GI Approximation")
                if scene.cycles.use_fast_gi:
                    row.prop(scene.cycles, "ao_bounces", text="Viewport Bounces")
                    row.prop(scene.cycles, "ao_bounces_render", text="Render Bounces")
            else :
                row = renderset_box.row(align=True)
                #row.scale_y = 1.5 # 缩小行的高度
                col_label = row.column()
                col_label.scale_x = 1.0#
                col_label.label(text='Cycles才有光程', icon="ERROR")#光程
                col0_prop = row.column()
                col0_prop.prop(scene.render, "engine", text="Render Engine")
                
            layout.separator()            
                  
class SCENE_OT_SyncLightPaths(bpy.types.Operator):#同步光程
    bl_idname = "scene.sync_light_paths"
    bl_label = ""
    bl_description = "Synchronize the light path settings of this scene to other scenes"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    scene_index: bpy.props.IntProperty()

    def execute(self, context):
        scenes = bpy.data.scenes
        source_scene = scenes[self.scene_index]

        for index, scene in enumerate(scenes):
            if index != self.scene_index:
                if source_scene.render.engine == 'CYCLES' and scene.render.engine == 'CYCLES':
                    # Cycles 渲染引擎的光程参数同步
                    scene.cycles.max_bounces = source_scene.cycles.max_bounces
                    scene.cycles.diffuse_bounces = source_scene.cycles.diffuse_bounces
                    scene.cycles.glossy_bounces = source_scene.cycles.glossy_bounces
                    scene.cycles.transmission_bounces = source_scene.cycles.transmission_bounces
                    scene.cycles.volume_bounces = source_scene.cycles.volume_bounces
                    scene.cycles.transparent_max_bounces = source_scene.cycles.transparent_max_bounces
                    scene.cycles.use_fast_gi = source_scene.cycles.use_fast_gi
                    scene.cycles.ao_bounces = source_scene.cycles.ao_bounces
                    scene.cycles.ao_bounces_render = source_scene.cycles.ao_bounces_render    
                    scene.cycles.caustics_reflective = source_scene.cycles.caustics_reflective#焦散反射
                    scene.cycles.caustics_refractive = source_scene.cycles.caustics_refractive#焦散折射
        
        return {'FINISHED'}

class SAMPLES_PT_Panel(bpy.types.Panel):#渲染采样
    bl_idname = "SAMPLES_PT_Panel"
    bl_label = "Samples"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SyncRenderSets'
    bl_order = 2  # 面板的显示顺序
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def draw(self, context):
        layout = self.layout
        scenes = bpy.data.scenes
        
        for scene in scenes:
            row = layout.row(align=True)
            col_label = row.column()
            col_label.scale_x = 1.5#
            scene_icon = "SCENE_DATA"  # 默认图标
            scene_txt = ""  # 默认文字
            if scene.name == bpy.context.scene.name:
                scene_icon = "FUND"  # 当前场景的图标
                scene_txt = "【Current】"
                col_label.alert = True
            col_label.label(text= f" {scene.name}" + scene_txt, icon=scene_icon)  # 场景名称
            col0_prop = row.column()
            col0_prop.operator("scene.sync_samples", text="Sync", icon="UV_SYNC_SELECT").scene_index = scenes.find(scene.name)        

            renderset_box = layout.box()#整体box            

        # 渲染采样面板box_997DD = box_996DB.box()
            if scene.render.engine == 'CYCLES':
                sampling_box = renderset_box.box()
                row = sampling_box.row(align=True)
                #row.scale_y = 1.5 # 缩小行的高度
                col_label = row.column()
                col_label.scale_x = 1.0#
                col_label.label(text='Render Samples')#渲染采样
                
                col_prop = row.column()
                col_prop.prop(scene.cycles, "use_adaptive_sampling", text="Noise Threshold")#噪波阈值
                if scene.cycles.use_adaptive_sampling:
                    col1_prop = row.column()
                    col1_prop.prop(scene.cycles, "adaptive_threshold", text="")#噪波阈值123
                    
                    row = sampling_box.row(heading='', align=True)
                    row.prop(scene.cycles, "samples", text="Max Samples")
                    row.prop(scene.cycles, "adaptive_min_samples", text="Min Samples")
                    row.prop(scene.cycles, "time_limit", text="Time Limit")
                
                else:
                    col1_prop = row.column()
                    col1_prop.label(text='Noise Threshold', icon='UNLINKED') 
               
                    row = sampling_box.row(heading='', align=True)
                    row.prop(scene.cycles, "samples", text="Samples")
                    row.prop(scene.cycles, "time_limit", text="Time Limit")
                
                row_1 = renderset_box.row()
                row_1.prop(scene.cycles, "use_denoising", text="Denoise")#渲染降噪
                row_1.prop(scene.render, "film_transparent")#胶片透明Film Transparent
                if scene.render.film_transparent:
                    row_1.prop(scene.cycles, "film_transparent_glass", text="Transparent Glass")  # 透明玻璃
                else:
                    row_1.label(text='Transparent Glass', icon='UNLINKED')
                row_1.prop(scene.render, "engine", text="")  # Render Engine
                if scene.render.engine == 'CYCLES':
                   row_1.prop(scene.cycles, "device", text="")  # Device
                layout.separator()
                    
            elif scene.render.engine == 'BLENDER_EEVEE':
                sampling_box = renderset_box.box()
                row = sampling_box.row(align=True)
                #row.scale_y = 1.5 # 缩小行的高度
                col_label = row.column()
                col_label.scale_x = 1.0#
                col_label.label(text='Render Samples')#渲染采样
                col_label.prop(scene.eevee, "use_taa_reprojection", text="Viewport Denoising")
                col_label.prop(scene.render, "engine", text="")    
                col_prop = row.column()
                col_prop.prop(scene.eevee, "taa_render_samples", text="Render")
                col1_prop = row.column()
                col1_prop.prop(scene.eevee, "taa_samples", text="Viewport")

                layout.separator()

class SCENE_OT_SyncSamples(bpy.types.Operator):#同步采样
    bl_idname = "scene.sync_samples"
    bl_label = ""
    bl_description = "Synchronize the sampling settings of this scene to other scenes"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    scene_index: bpy.props.IntProperty()

    def execute(self, context):
        scenes = bpy.data.scenes
        source_scene = scenes[self.scene_index]

        for index, scene in enumerate(scenes):
            if index != self.scene_index:
                # 复制参数到其他场景
                scene.render.engine = source_scene.render.engine#同步渲染引擎
                if source_scene.render.engine == 'CYCLES' and scene.render.engine == 'CYCLES':
                    # Cycles 渲染引擎的参数同步
                    scene.cycles.device = source_scene.cycles.device  # 设备
                    scene.cycles.use_adaptive_sampling = source_scene.cycles.use_adaptive_sampling  # 使用自适应采样
                    scene.cycles.adaptive_threshold = source_scene.cycles.adaptive_threshold  # 自适应采样噪声阈值
                    scene.cycles.samples = source_scene.cycles.samples  # 最大采样数
                    scene.cycles.adaptive_min_samples = source_scene.cycles.adaptive_min_samples  # 自适应采样最小采样数
                    scene.cycles.time_limit = source_scene.cycles.time_limit  # 时间限制
                    scene.cycles.use_denoising = source_scene.cycles.use_denoising  # 使用降噪
                    scene.render.film_transparent = source_scene.render.film_transparent  # 胶片透明
                    scene.cycles.film_transparent_glass = source_scene.cycles.film_transparent_glass  # 透明玻璃
                    #同步没有在面板里的参数
                    scene.cycles.denoiser = source_scene.cycles.denoiser#降噪器同步
                    scene.cycles.denoising_input_passes = source_scene.cycles.denoising_input_passes#降噪通道
                   
                elif source_scene.render.engine == 'BLENDER_EEVEE' and scene.render.engine == 'BLENDER_EEVEE':
                    # Eevee 渲染引擎的参数同步
                    scene.eevee.use_taa_reprojection = source_scene.eevee.use_taa_reprojection  # 使用视口降噪
                    scene.eevee.taa_render_samples = source_scene.eevee.taa_render_samples  # 渲染采样数
                    scene.eevee.taa_samples = source_scene.eevee.taa_samples  # 视口采样数


        return {'FINISHED'}

class RESOLUTION_PT_Panel(bpy.types.Panel):#场景分辨率
    bl_idname = "RESOLUTION_PT_Panel"
    bl_label = "Resolution"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SyncRenderSets'
    bl_order = 1  # 面板的显示顺序
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def draw(self, context):
        layout = self.layout
        scenes = bpy.data.scenes
        
        for scene in scenes:
             #最终渲染尺寸
            rd = scene.render
            final_res_x = (rd.resolution_x * rd.resolution_percentage) / 100
            final_res_y = (rd.resolution_y * rd.resolution_percentage) / 100
            final_res_x_border = round(
                (final_res_x * (rd.border_max_x - rd.border_min_x)))
            final_res_y_border = round(
                (final_res_y * (rd.border_max_y - rd.border_min_y)))

            row = layout.row(align=True)
            col_label = row.column()
            col_label.scale_x = 1.5#
            scene_icon = "SCENE_DATA"  # 默认图标
            scene_txt = ""  # 默认文字
            if scene.name == bpy.context.scene.name:
                scene_icon = "FUND"  # 当前场景的图标
                scene_txt = "【Current】"
                col_label.alert = True
            col_label.label(text= f" {scene.name}" +"[{} x {}]".format(str(final_res_x)[:-2], str(final_res_y)[:-2]) , icon=scene_icon)  # 场景名称+ scene_txt

            col_prop = row.column()
            #col_prop.prop(scene.render, "engine", text="")  # Render Engine
            col_prop.operator("scene.sync_resolution", text="Sync",icon="UV_SYNC_SELECT").scene_index = scenes.find(scene.name)
       
        #分辨率面板    
            row_2CC4F = layout.box()          
            col = row_2CC4F.column(align=True)
            row = col.split(factor=0.4, align=True)
            row.prop(scene.render, "resolution_x", text="X")            
            row.prop(scene.render, "resolution_percentage", text="%") 
            row1 = col.split(factor=0.4, align=True)
            row1.prop(scene.render, "resolution_y", text="Y")           
            if scene.render.engine == 'CYCLES':
                row2 = row1.split(factor=0.1, align=True)
                row2.prop(scene.cycles, "use_auto_tile",icon_only=True)
                if scene.cycles.use_auto_tile== False:
                    row2.active = False
                row2.prop(scene.cycles, "tile_size")
            else:
                row1.label(text= "EEVEE NO Tile Size!")

class SCENE_OT_SyncResolution(bpy.types.Operator):#同步场景分辨率
    bl_idname = "scene.sync_resolution"
    bl_label = ""
    bl_description = "Synchronize the resolution of this scene to other scenes"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    scene_index: bpy.props.IntProperty()
    
    def execute(self, context):
        scenes = bpy.data.scenes
        source_scene = scenes[self.scene_index]
        resolution_x = source_scene.render.resolution_x
        resolution_y = source_scene.render.resolution_y
        resolution_percentage = source_scene.render.resolution_percentage        
        resolution_use_auto_tile = source_scene.cycles.use_auto_tile
        resolution_tile_size = source_scene.cycles.tile_size

        
        for index, scene in enumerate(scenes):
            if index != self.scene_index:
                scene.render.resolution_x = resolution_x
                scene.render.resolution_y = resolution_y
                scene.render.resolution_percentage = resolution_percentage
                if source_scene.render.engine == 'CYCLES' and scene.render.engine == 'CYCLES':
                    scene.cycles.use_auto_tile = resolution_use_auto_tile
                    scene.cycles.tile_size = resolution_tile_size
        
        return {'FINISHED'}

class VPASSES_PT_Panel(bpy.types.Panel):#视图层通道Sync
    bl_idname = "VPASSES_PT_Panel"
    bl_label = "Passes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'SyncRenderSets'
    bl_order = 0  # 面板的显示顺序
    bl_options = {'DEFAULT_CLOSED'}
    
    @classmethod
    def poll(cls, context):
        return context.scene is not None
    
    def draw(self, context):
            layout = self.layout
            scenes = bpy.data.scenes
            sorted_view_layers = []  # 存储排序后的视图层

            active_scene = bpy.context.scene
            active_view_layer = bpy.context.view_layer

            # 将当前场景的所有视图层添加到排序列表
            for view_layer in active_scene.view_layers:
                sorted_view_layers.append((active_scene, view_layer))

            # 遍历其他场景和视图层，并添加到排序列表
            for scene in scenes:
                if scene != active_scene:
                    for view_layer in scene.view_layers:
                        sorted_view_layers.append((scene, view_layer))

            # 将当前视图层移到排序列表的首位
            sorted_view_layers.remove((active_scene, active_view_layer))
            sorted_view_layers.insert(0, (active_scene, active_view_layer))

            # 绘制排序后的视图层
            for scene, view_layer in sorted_view_layers:
                row = layout.row(align=True)
                col_label = row.column()
                col_label.scale_x = 1.5
                scene_icon = "RENDERLAYERS"  # 默认图标
                scene_txt = ""  # 默认文字

                if view_layer.name == bpy.context.view_layer.name and scene.name == bpy.context.scene.name:
                    scene_icon = "FUND"  # 当前场景的图标
                    scene_txt = "【Current】"#Current当前
                    col_label.alert = True
        
                    col_label.label(text=f"{scene.name}:" + f"{view_layer.name}" +scene_txt , icon=scene_icon)
                    col_prop = row.column()
                    col_prop.scale_y = 1.0
                    col_prop.operator("viewlayer.sync_passes", text="Sync", icon="UV_SYNC_SELECT")
                else:
                    col_label.label(text=f"{scene.name}:" + f"{view_layer.name}", icon=scene_icon)

            
                pass_box = layout.box()#整体box

            # 数据
                #data_box = pass_box.box()  
                column = pass_box.column()

                row_1 = column.row(align=True)
                row_1.prop(view_layer, "use_pass_combined")#
                row_1.prop(view_layer, "use_pass_z")#
                row_1.prop(view_layer, "use_pass_mist")#
                row_1.prop(view_layer, "use_pass_normal")#
                if scene.render.engine == 'CYCLES':
                    row_1.prop(view_layer, "use_pass_object_index")

                row_2 = column.row(align=True)
                if scene.render.engine == 'CYCLES':
                    cycles_view_layer = view_layer.cycles
                    row_2.prop(cycles_view_layer, "denoising_store_passes", text="Denoising Data")
                    row_2.prop(view_layer, "use_pass_position")
                    row_2.prop(view_layer, "use_pass_uv")
                    row_2.prop(view_layer, "use_pass_vector")
                    row_2.prop(view_layer, "use_pass_material_index")
                
            #灯光
                #light_box = pass_box.box()  # 整体box
                column = pass_box.column()

                row_1 = column.row(align=True)
                row_1.label(text="Diffuse")#漫射
                row_1.prop(view_layer, "use_pass_diffuse_direct", text="Direct")
                if scene.render.engine == 'CYCLES':
                    row_1.prop(view_layer, "use_pass_diffuse_indirect", text="Indirect")
                row_1.prop(view_layer, "use_pass_diffuse_color", text="Color")

                row_2 = column.row(align=True) 
                if scene.render.engine == 'CYCLES':
                    row_2.label(text="Glossy")#光泽
                    row_2.prop(view_layer, "use_pass_glossy_direct", text="Direct")
                    row_2.prop(view_layer, "use_pass_glossy_indirect", text="Indirect")
                    row_2.prop(view_layer, "use_pass_glossy_color", text="Color")

                row_3 = column.row(align=True)               
                if scene.render.engine == 'CYCLES':
                    row_3.label(text="Transmission")#透射
                    row_3.prop(view_layer, "use_pass_transmission_direct", text="Direct")
                    row_3.prop(view_layer, "use_pass_transmission_indirect", text="Indirect")
                    row_3.prop(view_layer, "use_pass_transmission_color", text="Color")
                
                row_4 = column.row(align=True)
                row_4.label(text="Volume")#体积
                if scene.render.engine == 'CYCLES':
                    cycles_view_layer = view_layer.cycles
                    row_4.prop(cycles_view_layer, "use_pass_volume_direct", text="Direct")
                    row_4.prop(cycles_view_layer, "use_pass_volume_indirect", text="Indirect")
                if scene.render.engine == 'BLENDER_EEVEE':
                    row_4.prop(view_layer.eevee, "use_pass_volume_direct", text="Light")

                row_5 = column.row(align=True)
                row_5.label(text="Other")#其它
                row_5.prop(view_layer, "use_pass_emit", text="Emission")
                row_5.prop(view_layer, "use_pass_environment")
                row_5.prop(view_layer, "use_pass_ambient_occlusion", text="Ambient Occlusion")
                if scene.render.engine == 'CYCLES':
                    cycles_view_layer = view_layer.cycles                   
                    row_5.prop(cycles_view_layer, "use_pass_shadow_catcher")
                if scene.render.engine == 'BLENDER_EEVEE':
                    row_5.prop(view_layer, "use_pass_shadow") 
            
            #Cryptomatte       
                # cryptomatte_box = pass_box.box()  # 整体box
                # column = cryptomatte_box.column()
                row_6 = column.row(align=True)
                row_6.label(text="Cryptomatte")
                row_6.prop(view_layer, "use_pass_cryptomatte_object", text="Object")
                row_6.prop(view_layer, "use_pass_cryptomatte_material", text="Material")
                row_6.prop(view_layer, "use_pass_cryptomatte_asset", text="Asset")

            layout.separator()

class SyncOperator(bpy.types.Operator):
    bl_idname = "viewlayer.sync_passes"
    bl_label = "Sync"
    bl_description = "Synchronize the current viewlayer passes to other view layers"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        active_scene = bpy.context.scene
        active_view_layer = bpy.context.view_layer

        # 获取活动视图层的勾选状态
        active_passes = [
            attr
            for attr in dir(active_view_layer)
            if attr.startswith("use_pass") and getattr(active_view_layer, attr)
        ]

        # 同步勾选状态给其他视图层
        for scene in bpy.data.scenes:
            for view_layer in scene.view_layers:
                if scene != active_scene or view_layer != active_view_layer:
                    for attr in dir(view_layer):
                        if attr.startswith("use_pass"):
                            setattr(view_layer, attr, attr in active_passes)

        return {'FINISHED'}



classes = (COLORMAN_PT_Panel,
    LIGHTPATHS_PT_Panel,#光程
    SCENE_OT_SyncLightPaths,#同步光程
    SAMPLES_PT_Panel,
    SCENE_OT_SyncSamples,#同步采样
    RESOLUTION_PT_Panel, 
    SCENE_OT_SyncResolution,#同步场景分辨率
    VPASSES_PT_Panel,#视图层通道
    SyncOperator,#Sync
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
