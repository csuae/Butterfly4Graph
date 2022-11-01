#!/opt/anaconda3/bin/python

import math
import argparse

from Butterfly import ButterflyNet

def check_args(args):
    '''
    Check if the input args from cmd line is legal
    '''
    # check n_stage & type_list & pfx_list
    assert args.n_stage == len(args.type_list), "Number of stages does not match the length of switch nodes type list"
    if args.pfx_list is not None:
        assert args.n_stage == len(args.pfx_list), "Number of stages does not match the length of switch nodes prefix name list"

    # check switch nodes type_list
    for _ in args.type_list:
        assert _ == 2 or _ == 4, "Invalid value found in switch nodes type list, allowed values are 2 or 4"

    # check type_list & n_port
    product = math.prod(args.type_list)
    assert args.n_port == product, "Number of i/o ports derived from type_list does not match input argument n_port"
    assert args.n_port <= 256, "Invalid argument: n_port, supported number of ports should be no greater than 256"

    # check monitor definition
    assert args.monitor_def[0] >= 1280 and args.monitor_def[0] <= 3840, "Invalid monitor width, allowed range is 1280 to 3840"
    assert args.monitor_def[1] >= 720 and args.monitor_def[1] <= 2160, "Invalid monitor height, allowed range is 720 to 2160"

    return

def main():
    parser = argparse.ArgumentParser(description='Automatically Generating Network Topology for Hi-GP')
    parser.add_argument('-ns', '--n_stage', type=int, required=True, help='number of stages/ranks in the interconnection network')
    parser.add_argument('-np', '--n_port', type=int, required=True, help='number of i/o ports of the interconnection network, power of two')
    parser.add_argument('-tl', '--type_list', nargs='+', type=int, required=True, help='type list of switch nodes in stage ascending order')
    parser.add_argument('-df', '--monitor_def', nargs=2, type=int, required=True, help='definition (Width Height in pixels) of used monitor which will determine the canvas size etc, e.g. 1920 1080')
    
    parser.add_argument('--pfx_list', nargs='+', type=str, help='prefix name of the switch nodes in stage ascending order')
    parser.add_argument('--tcl_fn', type=str, help='output tcl command file name for automatic connection')

    args = parser.parse_args()
    check_args(args)

    bfNet = ButterflyNet(
        n_stage=args.n_stage,
        n_port=args.n_port,
        type_list=args.type_list,
        monitor_def=args.monitor_def,
        pfx_list=args.pfx_list,
        tcl_fn=args.tcl_fn
        )

    # bfNet.save_network_image()
    bfNet.gen_connect_tcl_as_file()

if __name__ == '__main__':
    main()
