# Imports
import bpy

from blendernc.blendernc.python_functions import netcdf_values, update_value_and_node_tree

from blendernc.blendernc.msg_errors import unselected_nc_var, unselected_nc_file

from collections import defaultdict

class BlenderNC_NT_resolution(bpy.types.Node):
    # === Basics ===
    # Description string
    '''NetCDF loading resolution '''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'netCDFResolution'
    # Label for nice name display
    bl_label = "Resolution"
    # Icon identifier
    bl_icon = 'MESH_GRID'
    blb_type = "NETCDF"

    blendernc_resolution: bpy.props.FloatProperty(name = 'Resolution', 
                                                min = 1, max = 100, 
                                                default = 50, step =100,
                                                update=update_value_and_node_tree,
                                                precision=0, options={'ANIMATABLE'})

    # Dataset requirements
    blendernc_dataset_identifier: bpy.props.StringProperty()
    blendernc_dict = defaultdict(None)

    # === Optional Functions ===
    # Initialization function, called when a new node is created.
    # This is the most common place to create the sockets for a node, as shown below.
    # NOTE: this is not the same as the standard __init__ function in Python, which is
    #       a purely internal Python method and unknown to the node system!
    def init(self, context):
        self.inputs.new('bNCnetcdfSocket',"Dataset")
        self.outputs.new('bNCnetcdfSocket',"Dataset")
        self.color = (0.4,0.4,0.8)
        self.use_custom_color = True

    # Copy function to initialize a copied node from an existing one.
    def copy(self, node):
        print("Copying from node ", node)

    # Free function to clean up on removal.
    def free(self):
        if self.blendernc_dataset_identifier!='':
            self.blendernc_dict.pop(self.blendernc_dataset_identifier)
        print("Removing node ", self, ", Goodbye!")

    # Additional buttons displayed on the node.
    def draw_buttons(self, context, layout):
        layout.prop(self, "blendernc_resolution")

    # Detail buttons in the sidebar.
    # If this function is not defined, the draw_buttons function is used instead
    def draw_buttons_ext(self, context, layout):
        pass

    # Optional: custom label
    # Explicit user label overrides this, but here we can define a label dynamically
    def draw_label(self):
        return "Resolution"

    def update(self):
        if self.inputs[0].is_linked and self.inputs[0].links:
            self.blendernc_dataset_identifier = self.inputs[0].links[0].from_socket.unique_identifier
            nc_dict = self.inputs[0].links[0].from_socket.dataset
            if self.blendernc_dataset_identifier == '' or len(nc_dict.keys()):
                self.blendernc_dataset_identifier = self.inputs[0].links[0].from_node.blendernc_dataset_identifier
                nc_dict = self.inputs[0].links[0].from_node.blendernc_dict.copy()
            
            # Check that nc_dict contains at least an unique identifier
            if self.blendernc_dataset_identifier in nc_dict.keys():
                self.blendernc_dict[self.blendernc_dataset_identifier] = nc_dict[self.blendernc_dataset_identifier].copy()
                # Check if user has selected a variable
                if 'selected_var' not in self.blendernc_dict[self.blendernc_dataset_identifier].keys():
                    bpy.context.window_manager.popup_menu(unselected_nc_var, title="Error", icon='ERROR')
                    self.inputs[0].links[0].from_socket.unlink(self.inputs[0].links[0])
                    return
                dataset = self.blendernc_dict[self.blendernc_dataset_identifier]['Dataset']
                var_name = self.blendernc_dict[self.blendernc_dataset_identifier]["selected_var"]['selected_var_name']
                self.blendernc_dict[self.blendernc_dataset_identifier]['Dataset'] = netcdf_values(dataset,var_name,self.blendernc_resolution)
            else: 
                bpy.context.window_manager.popup_menu(unselected_nc_file, title="Error", icon='ERROR')
                self.inputs[0].links[0].from_socket.unlink(self.inputs[0].links[0])
        else:
            if self.blendernc_dataset_identifier in self.blendernc_dict.keys() :
                self.blendernc_dict.pop(self.blendernc_dataset_identifier)
            
        if self.outputs.items():
            if self.outputs[0].is_linked and self.inputs[0].is_linked:
                self.outputs[0].dataset[self.blendernc_dataset_identifier] = self.blendernc_dict[self.blendernc_dataset_identifier].copy()
                self.outputs[0].unique_identifier = self.blendernc_dataset_identifier