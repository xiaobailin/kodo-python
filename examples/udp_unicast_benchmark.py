#! /usr/bin/env python
# encoding: utf-8

# Copyright Steinwurf ApS 2014.
# Distributed under the "STEINWURF RESEARCH LICENSE 1.0".
# See accompanying file LICENSE.rst or
# http://www.steinwurf.com/licensing

import sys
import argparse
import json
import itertools
import time

import udp_unicast

def get_settings(parameter_space, repeat = 1):
    """
    Returns a iterator that yelds all possible combinations in a dictionary of
    parameter, where each parameter is given a list of possible values.

    the parameter space is repeated "repeat" times

    Example:
    {"p1": [1,2], "p2": [3,4], "p3": [5]}

    return and iterator the yelds the following:
    {"p1": [1], "p2": [3], "p3": [5]}
    {"p1": [1], "p2": [4], "p3": [5]}
    {"p1": [2], "p2": [3], "p3": [5]}
    {"p1": [2], "p2": [4], "p3": [5]}
    """

    l = list()
    for key,value in parameter_space.iteritems():
        l.append( list( itertools.product([key],value)))

    settings = iter("")

    for r in range(repeat):
        settings = itertools.chain(settings, itertools.product(*l))

    return settings

def main():
    """
    UDP Server/Client benchmarking of a defined parameter space
    """

    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without network use, for testing purposes')

    subparsers = parser.add_subparsers(
        dest='role', help='help for subcommand')

    server_parser = subparsers.add_parser(
        'server',
        description="UDP server for sending and receiving files.",
        help='Start a server')

    server_parser.add_argument(
        '--settings-port',
        type=int,
        help='settings port on the server.',
        default=41001)

    client_parser = subparsers.add_parser(
        'client',
        description="UDP client for sending and receiving files.",
        help='Start a client')

    client_parser.add_argument(
        '--parameters-file',
        type=str,
        help='file containing test parameters',
        default='parameters.json')

    client_parser.add_argument(
        '--runs',
        type=int,
        help='number of times to run through the parameter space',
        default=1)

    client_parser.add_argument(
        '--print-parameters-used',
        type=bool,
        help='Print the parameters to be used instead of testing',
        default=False)

    # We have to use syg.argv for the dry-run parameter, otherwise a subcommand
    # is required.
    if '--dry-run' in sys.argv:
        return

    args = parser.parse_args()

    if args.role == 'client':

        parameter_space = json.load(open(args.parameters_file))

        # for run in range(args.runs):
        settings = get_settings(parameter_space, args.runs)
        for setting in settings:
            s = dict(setting)
            if args.print_parameters_used:
                print s
            else:
                udp_unicast.client(s)
                # sleep for a bit to ensure that sockets have time to close
                time.sleep(1)
    else: #server
        settings = vars(args)
        udp_unicast.server(settings)

if __name__ == "__main__":
    main()