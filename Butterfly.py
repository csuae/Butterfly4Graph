# Butterfly Network Based on 2X2 Node and 4X4 Node

import math
import matplotlib.pyplot as plt
from matplotlib import collections  as mc


class ButterflyNet(object):

    def __init__(self, n_stage=None, n_port=None, type_list=None, monitor_def=None, pfx_list=None, tcl_fn=None):
        self.n_stage = n_stage
        self.n_port = n_port
        self.type_list = type_list
        self.pfx_list = pfx_list
        self.tcl_fn = tcl_fn

        # baseline size is based on 2K definition (2560*1440)
        self.scale_factor = monitor_def[1] / 1440
        self.zoom_factor = 256 / self.n_port
        # horizontal and vertical margin of the (0, 0) switch node
        self.H_margin = 6.0
        self.V_margin = 1.0

        self.get_all_size()
        self.get_all_coordinates()
        self.get_pin_pairs()

        self.create_canvas()
        self.draw_switch_nodes()
        self.draw_pin_connection()

    def get_all_size(self):
        '''
        Get size(float) of canvas, switch nodes, spacing, line segments etc
        '''
        self.TNode_height = 0.8 * self.scale_factor * self.zoom_factor
        self.TNode_vspace = 0.18 * self.scale_factor * self.zoom_factor
        
        self.FNode_height = 1.6 * self.scale_factor * self.zoom_factor
        self.FNode_vspace = 0.36 * self.scale_factor * self.zoom_factor
        
        self.Node_width = 1.2 * (8 / self.n_stage)
        self.Node_hspace = 24.4 * self.scale_factor * (8 / self.n_stage)


    def get_all_coordinates(self):
        '''
        Get coordinates(float) of every switch node, including the central point and input/output pins
        '''
        # set the coordinate of the (0, 0) switch node
        x0 = self.H_margin + self.Node_width/2

        '''
        Create dictionary to record the coordinate of the central point
            Key: switch node tuples (i, j) as identifier of stage i and j_th switch node
            Value: one tuple of float value as (x, y) coordinate 
        '''
        self.dict_central_point_coord = {}
        for i in range(self.n_stage):
            # switch node travseral: stage i, j_th node
            n_nodes = self.n_port // self.type_list[i]
            y0 = self.V_margin + (self.TNode_height/2 if self.type_list[i] == 2 else self.FNode_height/2)

            for j in range(n_nodes):
                x = x0 + i * self.Node_hspace
                if self.type_list[i] == 2:
                    y = y0 + j * self.TNode_height + j//2 * self.FNode_vspace
                else:
                    y = y0 + j * (self.FNode_height+self.FNode_vspace)

                self.dict_central_point_coord[(i, j)] = (x, y)


        hw = self.Node_width / 2
        z = self.zoom_factor

        hqw = hw * 1.5
        '''
        Create dictionary to record the coordinate of the input pins
            Key: switch node tuples (i, j) as identifier of stage i and j_th switch node
            Value: one list consists of two/four tuples, each of float value as (x, y) coordinate
            Note: with the same key, the tuples are organized in y-coordinate ascending order
        '''
        self.dict_input_pin_coord = {}
        for i in range(self.n_stage):
            # switch node travseral: stage i, j_th node
            n_nodes = self.n_port // self.type_list[i]

            xi = self.dict_central_point_coord[(i, 0)][0]
            x = xi - hqw
            for j in range(n_nodes):
                yj = self.dict_central_point_coord[(i, j)][1]
                self.dict_input_pin_coord[(i, j)] = []
                
                if self.type_list[i] == 2:
                    self.dict_input_pin_coord[(i, j)].append((x, yj - 0.2*z*self.scale_factor))
                    self.dict_input_pin_coord[(i, j)].append((x, yj + 0.2*z*self.scale_factor))
                else:
                    self.dict_input_pin_coord[(i, j)].append((x, yj - 0.6*z*self.scale_factor))
                    self.dict_input_pin_coord[(i, j)].append((x, yj - 0.2*z*self.scale_factor))
                    self.dict_input_pin_coord[(i, j)].append((x, yj + 0.2*z*self.scale_factor))
                    self.dict_input_pin_coord[(i, j)].append((x, yj + 0.6*z*self.scale_factor))

        '''
        Create dictionary to record the coordinate of the output pins
            Key: switch node tuples (i, j) as identifier of stage i and j_th switch node
            Value: one list consists of two/four tuples, each of float value as (x, y) coordinate
            Note: with the same key, the tuples are organized in y-coordinate ascending order
        '''
        self.dict_output_pin_coord = {}
        for i in range(self.n_stage):
            # switch node travseral: stage i, j_th node
            n_nodes = self.n_port // self.type_list[i]

            xi = self.dict_central_point_coord[(i, 0)][0]
            x = xi + hqw
            for j in range(n_nodes):
                yj = self.dict_central_point_coord[(i, j)][1]
                self.dict_output_pin_coord[(i, j)] = []
                
                if self.type_list[i] == 2:
                    self.dict_output_pin_coord[(i, j)].append((x, yj - 0.2*z*self.scale_factor))
                    self.dict_output_pin_coord[(i, j)].append((x, yj + 0.2*z*self.scale_factor))
                else:
                    self.dict_output_pin_coord[(i, j)].append((x, yj - 0.6*z*self.scale_factor))
                    self.dict_output_pin_coord[(i, j)].append((x, yj - 0.2*z*self.scale_factor))
                    self.dict_output_pin_coord[(i, j)].append((x, yj + 0.2*z*self.scale_factor))
                    self.dict_output_pin_coord[(i, j)].append((x, yj + 0.6*z*self.scale_factor))


    def get_pin_pairs(self):
        ''' 
        Get all pin pairs for connection in the next step
            Firstly, build (uniSrcId, uniDstId) pairs, then convert to
            From (srcSwId, srcPortId) to (dstSwId, dstPortId)
        '''
        list_uni_pairs = [[] for i in range(self.n_stage-1)]
        # create (uniSrcId, uniDstId) tuples as pin pairs
        for i in range(self.n_stage-1):
            pre_span = self.n_port // math.prod(self.type_list[0:i])
            cur_span = self.n_port // math.prod(self.type_list[0:i+1])

            # traverse across all switch nodes from i_th stage
            n_ports = self.type_list[i]
            n_nodes = self.n_port // n_ports
            for j in range(n_nodes):
                uniId_ofst = j*n_ports // pre_span * pre_span
                for k in range(n_ports):
                    uniSrcId = j*n_ports + k
                    rank = (uniSrcId%pre_span) // cur_span
                    if k == rank:
                        fxPortId = k

                for l in range(n_ports):
                    uniSrcId = j*n_ports + (fxPortId+l)%n_ports
                    uniDstId = uniId_ofst + (j*n_ports+fxPortId + cur_span*l) % pre_span

                    list_uni_pairs[i].append((uniSrcId, uniDstId))
        # print(list_uni_pairs)


        '''
        Create dictionary to record the connection pairs between output pins of i_th stage and input pins of i+1_th stage
            Key: stage Id tuples (i, i+1)
            Value: list of lists, each inner list consists of [(srcSwId, srcPortId), (dstSwId, dstPortId)] as a [src, dst] list
        '''
        self.dict_connect_pin_pairs = {}
        # convert uniId to (SwId, PortId) tuple
        for i in range(self.n_stage-1):
            self.dict_connect_pin_pairs[(i, i+1)] = []

            # traverse across all pin pairs within one list
            for srcId, dstId in list_uni_pairs[i]:
                srcSwId = srcId // self.type_list[i]
                srcPortId = srcId % self.type_list[i]

                dstSwId = dstId // self.type_list[i+1]
                dstPortId = dstId % self.type_list[i+1]

                self.dict_connect_pin_pairs[(i, i+1)].append([(srcSwId, srcPortId), (dstSwId, dstPortId)])


    def create_canvas(self):
        '''
        In 2K monitor definition baseline, canvas size is 1280 (Width) * 2160 (Height) in pixels
        '''
        Width = 216.0 * self.scale_factor
        Height= 128.0 * self.scale_factor

        plt.figure(figsize=[Width, Height], dpi=10)

        self.ax = plt.subplot(111,aspect = 'equal')
        self.ax.set_xlim([0, Width])
        self.ax.set_ylim([0, Height])

        plt.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)


    def draw_switch_nodes(self):
        '''
        Draw switch nodes (edges) and their corresponding i/o pins by matplotlib
            Top Edge -a; Bottom Edge - b; Left Edge - c; Right Edge - d
        '''
        # create coordinate pairs for edges of switch nodes
        list_edge_a_pairs = [[] for i in range(self.n_stage)]
        list_edge_b_pairs = [[] for i in range(self.n_stage)]
        list_edge_c_pairs = [[] for i in range(self.n_stage)]
        list_edge_d_pairs = [[] for i in range(self.n_stage)]

        hw = self.Node_width / 2
        z = self.zoom_factor

        hqw = hw * 1.5
        for i in range(self.n_stage):
            # switch node travseral: stage i, j_th node
            n_nodes = self.n_port // self.type_list[i]        
            
            xi = self.dict_central_point_coord[(i, 0)][0]
            for j in range(n_nodes):
                yj = self.dict_central_point_coord[(i, j)][1]
                if self.type_list[i] == 2:
                    list_edge_a_pairs[i].append([(xi-hw, yj-0.4*z*self.scale_factor), (xi+hw, yj-0.4*z*self.scale_factor)])
                    list_edge_b_pairs[i].append([(xi-hw, yj+0.4*z*self.scale_factor), (xi+hw, yj+0.4*z*self.scale_factor)])
                    list_edge_c_pairs[i].append([(xi-hw, yj-0.4*z*self.scale_factor), (xi-hw, yj+0.4*z*self.scale_factor)])
                    list_edge_d_pairs[i].append([(xi+hw, yj-0.4*z*self.scale_factor), (xi+hw, yj+0.4*z*self.scale_factor)])
                else:
                    list_edge_a_pairs[i].append([(xi-hw, yj-0.8*z*self.scale_factor), (xi+hw, yj-0.8*z*self.scale_factor)])
                    list_edge_b_pairs[i].append([(xi-hw, yj+0.8*z*self.scale_factor), (xi+hw, yj+0.8*z*self.scale_factor)])
                    list_edge_c_pairs[i].append([(xi-hw, yj-0.8*z*self.scale_factor), (xi-hw, yj+0.8*z*self.scale_factor)])
                    list_edge_d_pairs[i].append([(xi+hw, yj-0.8*z*self.scale_factor), (xi+hw, yj+0.8*z*self.scale_factor)])

        # create coordinate pairs for i/o pins of switch nodes
        list_input_pin_pairs = [[] for i in range(self.n_stage)]
        list_output_pin_pairs = [[] for i in range(self.n_stage)]
        
        for i in range(self.n_stage):
            # switch node travseral: stage i, j_th node
            n_nodes = self.n_port // self.type_list[i]        
            
            xi = self.dict_central_point_coord[(i, 0)][0]
            for j in range(n_nodes):
                yj = self.dict_central_point_coord[(i, j)][1]
                if self.type_list[i] == 2:
                    list_input_pin_pairs[i].append([(xi-hqw, yj-0.2*z*self.scale_factor), (xi-hw, yj-0.2*z*self.scale_factor)])
                    list_input_pin_pairs[i].append([(xi-hqw, yj+0.2*z*self.scale_factor), (xi-hw, yj+0.2*z*self.scale_factor)])

                    list_output_pin_pairs[i].append([(xi+hw, yj-0.2*z*self.scale_factor), (xi+hqw, yj-0.2*z*self.scale_factor)])
                    list_output_pin_pairs[i].append([(xi+hw, yj+0.2*z*self.scale_factor), (xi+hqw, yj+0.2*z*self.scale_factor)])
                else:
                    list_input_pin_pairs[i].append([(xi-hqw, yj-0.6*z*self.scale_factor), (xi-hw, yj-0.6*z*self.scale_factor)])
                    list_input_pin_pairs[i].append([(xi-hqw, yj-0.2*z*self.scale_factor), (xi-hw, yj-0.2*z*self.scale_factor)])
                    list_input_pin_pairs[i].append([(xi-hqw, yj+0.2*z*self.scale_factor), (xi-hw, yj+0.2*z*self.scale_factor)])
                    list_input_pin_pairs[i].append([(xi-hqw, yj+0.6*z*self.scale_factor), (xi-hw, yj+0.6*z*self.scale_factor)])

                    list_output_pin_pairs[i].append([(xi+hw, yj-0.6*z*self.scale_factor), (xi+hqw, yj-0.6*z*self.scale_factor)])
                    list_output_pin_pairs[i].append([(xi+hw, yj-0.2*z*self.scale_factor), (xi+hqw, yj-0.2*z*self.scale_factor)])
                    list_output_pin_pairs[i].append([(xi+hw, yj+0.2*z*self.scale_factor), (xi+hqw, yj+0.2*z*self.scale_factor)])
                    list_output_pin_pairs[i].append([(xi+hw, yj+0.6*z*self.scale_factor), (xi+hqw, yj+0.6*z*self.scale_factor)])

        # draw edges and i/o pins
        for i in range(self.n_stage):
            lc_edge_a = mc.LineCollection(list_edge_a_pairs[i], colors='k', linewidth=8)
            lc_edge_b = mc.LineCollection(list_edge_b_pairs[i], colors='k', linewidth=8)
            lc_edge_c = mc.LineCollection(list_edge_c_pairs[i], colors='k', linewidth=8)
            lc_edge_d = mc.LineCollection(list_edge_d_pairs[i], colors='k', linewidth=8)

            self.ax.add_collection(lc_edge_a)
            self.ax.add_collection(lc_edge_b)
            self.ax.add_collection(lc_edge_c)
            self.ax.add_collection(lc_edge_d)

            lc_input_pin = mc.LineCollection(list_input_pin_pairs[i], colors='k', linewidth=6)
            lc_output_pin = mc.LineCollection(list_output_pin_pairs[i], colors='k', linewidth=6)

            self.ax.add_collection(lc_input_pin)
            self.ax.add_collection(lc_output_pin)


    def draw_pin_connection(self):
        '''
        Draw the connection line segments among pins by matplotlib
        '''
        for i in range(self.n_stage-1):
            # convert pin pairs to coordinate pairs i.e. (SwId, PortId) to (x, y)
            list_pin_pairs = []
            
            pin_pairs = self.dict_connect_pin_pairs[(i, i+1)]
            for pair in pin_pairs:
                src_pin = pair[0]
                dst_pin = pair[1]

                src_pin_coord = self.dict_output_pin_coord[(i, src_pin[0])][src_pin[1]]
                dst_pin_coord = self.dict_input_pin_coord[(i+1, dst_pin[0])][dst_pin[1]]
                list_pin_pairs.append([src_pin_coord, dst_pin_coord])

            lc = mc.LineCollection(list_pin_pairs, colors='b', linewidth=6)
            self.ax.add_collection(lc)


    def save_network_image(self):
        '''
        Save the butterfly network topology image as file
        '''
        str_type_list = ''
        for i in range(self.n_stage):
            str_type_list = str_type_list + '_' + str(self.type_list[i])
        
        img_fn = 'ButterflyNet_%dX%d%s' % (self.n_port, self.n_port, str_type_list)
        # img_fn = 'ButterflyNet_' + str(self.n_port) + 'X' + str(self.n_port) + '_' + str_type_list
        plt.savefig(img_fn)



    def gen_connect_tcl_as_file(self):
        '''
        Generate the tcl command for automatic connection as file
            Tcl cmd <create external ports>: make_bd_pins_external  [get_bd_pins <IP_Instance>/<Pin>]
            Tcl cmd <rename external ports>: set_property name <new_name> [get_bd_ports <old_name>]
            Tcl cmd <connect external ports>: connect_bd_net [get_bd_ports <ext_port>] [get_bd_pins <IP_Instance>/<Pin>]
            Tcl cmd <connect two pins>: connect_bd_net [get_bd_pins <IP_Instance_a>/<Pin_a>] [get_bd_pins <IP_Instance_b>/<Pin_b>]
        '''
        assert self.tcl_fn is not None, "Output tcl command file name not specified"

        self.gen_tcl_crt_rn_ext_ports() # create & rename external ports
        self.gen_tcl_connect_clk_rst() # connect clk & rst_n signals

        for stageIdx in range(self.n_stage-1):
            self.gen_tcl_connect_consec_stages(stageIdx)


    def gen_tcl_crt_rn_ext_ports(self):
        
        with open(self.tcl_fn, 'w') as file:
            file.write('startgroup\n')

            cmd_ext_clk = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_0/clk]\n'
            cmd_ext_rst = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_0/rst_n]\n'
            file.write(cmd_ext_clk)
            file.write(cmd_ext_rst)

            # ivld signals
            for i in range(self.n_port):
                if (self.type_list[0] == 2):
                    cmd_crt_ivld = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_'+str(i//2)+'/ivld_'+chr(ord('a')+i%2)+']\n'
                else:
                    cmd_crt_ivld = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_'+str(i//4)+'/ivld_'+chr(ord('a')+i%4)+']\n'
                
                file.write(cmd_crt_ivld)
            
            file.write('\n')
            
            # din signals
            for i in range(self.n_port):
                if (self.type_list[0] == 2):
                    cmd_crt_din = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_'+str(i//2)+'/din_'+chr(ord('a')+i%2)+']\n'
                else:
                    cmd_crt_din = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_'+str(i//4)+'/din_'+chr(ord('a')+i%4)+']\n'
                
                file.write(cmd_crt_din)
            
            file.write('\n')
            
            # ofw signals
            for i in range(self.n_port):
                if (self.type_list[0] == 2):
                    cmd_crt_ofw = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_'+str(i//2)+'/ofw_input_'+chr(ord('a')+i%2)+']\n'
                else:
                    cmd_crt_ofw = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[0] +'_'+str(i//4)+'/ofw_input_'+chr(ord('a')+i%4)+']\n'
                
                file.write(cmd_crt_ofw)
            
            file.write('\n')

            # ovld signals
            for i in range(self.n_port):
                if (self.type_list[self.n_stage-1] == 2):
                    cmd_crt_ovld = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[self.n_stage-1] +'_'+str(i//2)+'/ovld_'+chr(ord('a')+i%2)+']\n'
                else:
                    cmd_crt_ovld = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[self.n_stage-1] +'_'+str(i//4)+'/ovld_'+chr(ord('a')+i%4)+']\n'
                
                file.write(cmd_crt_ovld)
            
            file.write('\n')

            # dout signals
            for i in range(self.n_port):
                if (self.type_list[self.n_stage-1] == 2):
                    cmd_crt_dout = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[self.n_stage-1] +'_'+str(i//2)+'/dout_'+chr(ord('a')+i%2)+']\n'
                else:
                    cmd_crt_dout = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[self.n_stage-1] +'_'+str(i//4)+'/dout_'+chr(ord('a')+i%4)+']\n'
                
                file.write(cmd_crt_dout)
            
            file.write('\n')

            # bp signals
            for i in range(self.n_port):
                if (self.type_list[self.n_stage-1] == 2):
                    cmd_crt_bp = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[self.n_stage-1] +'_'+str(i//2)+'/ofw_output_'+chr(ord('a')+i%2)+']\n'
                else:
                    cmd_crt_bp = 'make_bd_pins_external  [get_bd_pins '+ self.pfx_list[self.n_stage-1] +'_'+str(i//4)+'/ofw_output_'+chr(ord('a')+i%4)+']\n'
                
                file.write(cmd_crt_bp)
            
            file.write('endgroup\n\n\n')

        '''
        Rename External Ports
        '''
        with open(self.tcl_fn, 'a') as file:
            file.write('startgroup\n')

            cmd_ext_clk = 'set_property name clk [get_bd_ports clk_0]\n'
            cmd_ext_rst = 'set_property name rst_n [get_bd_ports rst_n_0]\n'
            file.write(cmd_ext_clk)
            file.write(cmd_ext_rst)

            # ivld signals
            for i in range(self.n_port):
                if (self.type_list[0] == 2):
                    cmd_rn_ivld = 'set_property name ivld_'+str(i)+' [get_bd_ports ivld_'+chr(ord('a')+i%2)+'_'+str(i//2)+']\n'
                else:
                    cmd_rn_ivld = 'set_property name ivld_'+str(i)+' [get_bd_ports ivld_'+chr(ord('a')+i%4)+'_'+str(i//4)+']\n'
                
                file.write(cmd_rn_ivld)
            
            file.write('\n')

            # din signals
            for i in range(self.n_port):
                if (self.type_list[0] == 2):
                    cmd_rn_din = 'set_property name din_'+str(i)+' [get_bd_ports din_'+chr(ord('a')+i%2)+'_'+str(i//2)+']\n'
                else:
                    cmd_rn_din = 'set_property name din_'+str(i)+' [get_bd_ports din_'+chr(ord('a')+i%4)+'_'+str(i//4)+']\n'
                
                file.write(cmd_rn_din)
            
            file.write('\n')

            # ofw signals
            for i in range(self.n_port):
                if (self.type_list[0] == 2):
                    cmd_rn_ofw = 'set_property name ofw_'+str(i)+' [get_bd_ports ofw_input_'+chr(ord('a')+i%2)+'_'+str(i//2)+']\n'
                else:
                    cmd_rn_ofw = 'set_property name ofw_'+str(i)+' [get_bd_ports ofw_input_'+chr(ord('a')+i%4)+'_'+str(i//4)+']\n'
                
                file.write(cmd_rn_ofw)
            
            file.write('\n')


            # ovld signals
            for i in range(self.n_port):
                if (self.type_list[self.n_stage-1] == 2):
                    cmd_rn_ovld = 'set_property name ovld_'+str(i)+' [get_bd_ports ovld_'+chr(ord('a')+i%2)+'_'+str(i//2)+']\n'
                else:
                    cmd_rn_ovld = 'set_property name ovld_'+str(i)+' [get_bd_ports ovld_'+chr(ord('a')+i%4)+'_'+str(i//4)+']\n'
                
                file.write(cmd_rn_ovld)
            
            file.write('\n')

            # dout signals
            for i in range(self.n_port):
                if (self.type_list[self.n_stage-1] == 2):
                    cmd_rn_dout = 'set_property name dout_'+str(i)+' [get_bd_ports dout_'+chr(ord('a')+i%2)+'_'+str(i//2)+']\n'
                else:
                    cmd_rn_dout = 'set_property name dout_'+str(i)+' [get_bd_ports dout_'+chr(ord('a')+i%4)+'_'+str(i//4)+']\n'
                
                file.write(cmd_rn_dout)
            
            file.write('\n')

            # bp signals
            for i in range(self.n_port):
                if (self.type_list[self.n_stage-1] == 2):
                    cmd_rn_bp = 'set_property name bp_'+str(i)+' [get_bd_ports ofw_output_'+chr(ord('a')+i%2)+'_'+str(i//2)+']\n'
                else:
                    cmd_rn_bp = 'set_property name bp_'+str(i)+' [get_bd_ports ofw_output_'+chr(ord('a')+i%4)+'_'+str(i//4)+']\n'
                
                file.write(cmd_rn_bp)
            
            file.write('endgroup\n\n\n')


    def gen_tcl_connect_clk_rst(self):

        with open(self.tcl_fn, 'a') as file:

            for i in range(self.n_stage):
                n_nodes = self.n_port // self.type_list[i]
                for j in range(n_nodes):
                    if not (i==0 and j==0):
                        cmd_clk = 'connect_bd_net [get_bd_ports clk] [get_bd_pins '+ self.pfx_list[i] +'_'+str(j)+'/clk]\n'
                        cmd_rst = 'connect_bd_net [get_bd_ports rst_n] [get_bd_pins '+ self.pfx_list[i] +'_'+str(j)+'/rst_n]\n'

                        file.write(cmd_clk)
                        file.write(cmd_rst)
                
                file.write('\n')


    def gen_tcl_connect_consec_stages(self, stageIdx):
        '''
        Connect pins between stage stageIdx and stageIdx+1
        '''
        # list of [(srcSwId, srcPortId), (dstSwId, dstPortId)] lists
        pin_pairs = self.dict_connect_pin_pairs[(stageIdx, stageIdx+1)]

        # ovld to ivld
        with open(self.tcl_fn, 'a') as file:
            file.write('startgroup\n')
            for pair in pin_pairs:
                src_pin = pair[0] # srcSwId: src_pin[0]; srcPortId: src_pin[1]
                dst_pin = pair[1] # dstSwId: dst_pin[0]; dstPortId: dst_pin[1]

                cmd = 'connect_bd_net [get_bd_pins '+self.pfx_list[stageIdx]+'_'+str(src_pin[0])+'/ovld_'+chr(ord('a')+src_pin[1])+'] ' \
				'[get_bd_pins '+self.pfx_list[stageIdx+1]+'_'+str(dst_pin[0])+'/ivld_'+chr(ord('a')+dst_pin[1])+']\n'

                file.write(cmd)

            file.write('\n')

        # dout to din
        with open(self.tcl_fn, 'a') as file:
            for pair in pin_pairs:
                src_pin = pair[0] # srcSwId: src_pin[0]; srcPortId: src_pin[1]
                dst_pin = pair[1] # dstSwId: dst_pin[0]; dstPortId: dst_pin[1]

                cmd = 'connect_bd_net [get_bd_pins '+self.pfx_list[stageIdx]+'_'+str(src_pin[0])+'/dout_'+chr(ord('a')+src_pin[1])+'] ' \
				'[get_bd_pins '+self.pfx_list[stageIdx+1]+'_'+str(dst_pin[0])+'/din_'+chr(ord('a')+dst_pin[1])+']\n'

                file.write(cmd)

            file.write('\n')

        # ofw_input to ofw_output
        with open(self.tcl_fn, 'a') as file:
            for pair in pin_pairs:
                src_pin = pair[0] # srcSwId: src_pin[0]; srcPortId: src_pin[1]
                dst_pin = pair[1] # dstSwId: dst_pin[0]; dstPortId: dst_pin[1]

                cmd = 'connect_bd_net [get_bd_pins '+self.pfx_list[stageIdx]+'_'+str(src_pin[0])+'/ofw_output_'+chr(ord('a')+src_pin[1])+'] ' \
				'[get_bd_pins '+self.pfx_list[stageIdx+1]+'_'+str(dst_pin[0])+'/ofw_input_'+chr(ord('a')+dst_pin[1])+']\n'

                file.write(cmd)

            file.write('\n')
            
            file.write('endgroup\n\n')

