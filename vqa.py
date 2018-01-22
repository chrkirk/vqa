from functools import partial
import sys
import os

import numpy as np

from vmaf.config import VmafConfig, DisplayConfig
from vmaf.core.asset import Asset
from vmaf.core.quality_runner import VmafQualityRunner, \
                                     PsnrQualityRunner
from vmaf.tools.misc import get_file_name_without_extension, \
                            get_cmd_option, \
                            cmd_option_exists
from vmaf.tools.stats import ListStats

FMTS = ['yuv420p', 'yuv422p', 'yuv444p', 'yuv420p10le', 'yuv422p10le', 'yuv444p10le']
POOL_METHODS = ['mean', 'harmonic_mean', 'min', 'median', 'perc5', 'perc10', 'perc20']

def run_vmaf(ref_path, dis_path, width, height, fmt, phone_model=False, pool_method=None):
    asset = Asset(dataset="cmd",
                  content_id=abs(hash(get_file_name_without_extension(ref_path))) % (10 ** 16),
                  asset_id=abs(hash(get_file_name_without_extension(ref_path))) % (10 ** 16),
                  workdir_root=VmafConfig.workdir_path(),
                  ref_path=ref_path,
                  dis_path=dis_path,
                  asset_dict={'width':width, 'height':height, 'yuv_type':fmt}
                  )
    assets = [asset]

    # I won't be using a model
    optional_dict = {}
    if phone_model:
        optional_dict['enable_transform_score'] = True

    runner_class = VmafQualityRunner
    runner = runner_class(
        assets, None, fifo_mode=True,
        delete_workdir=True,
        result_store=None,
        optional_dict=optional_dict,
        optional_dict2=None,
    )

    # run
    runner.run()
    result = runner.results[0]

    # pooling
    if pool_method == 'harmonic_mean':
        result.set_score_aggregate_method(ListStats.harmonic_mean)
    elif pool_method == 'min':
        result.set_score_aggregate_method(np.min)
    elif pool_method == 'median':
        result.set_score_aggregate_method(np.median)
    elif pool_method == 'perc5':
        result.set_score_aggregate_method(ListStats.perc5)
    elif pool_method == 'perc10':
        result.set_score_aggregate_method(ListStats.perc10)
    elif pool_method == 'perc20':
        result.set_score_aggregate_method(ListStats.perc20)
    else: # None or 'mean'
        pass
    return result.result_dict


def run_psnr(ref_path, dis_path, width, height, fmt, pool_method=None):
    asset = Asset(dataset="cmd", content_id=0, asset_id=0,
                  workdir_root=VmafConfig.workdir_path(),
                  ref_path=ref_path,
                  dis_path=dis_path,
                  asset_dict={'width':width, 'height':height, 'yuv_type':fmt}
                  )
    assets = [asset]

    runner_class = PsnrQualityRunner

    runner = runner_class(
        assets, None, fifo_mode=True,
        delete_workdir=True,
        result_store=None,
        optional_dict=None,
        optional_dict2=None,
    )

    # run
    runner.run()
    result = runner.results[0]

    # pooling
    if pool_method == 'harmonic_mean':
        result.set_score_aggregate_method(ListStats.harmonic_mean)
    elif pool_method == 'min':
        result.set_score_aggregate_method(np.min)
    elif pool_method == 'median':
        result.set_score_aggregate_method(np.median)
    elif pool_method == 'perc5':
        result.set_score_aggregate_method(ListStats.perc5)
    elif pool_method == 'perc10':
        result.set_score_aggregate_method(ListStats.perc10)
    elif pool_method == 'perc20':
        result.set_score_aggregate_method(ListStats.perc20)
    else: # None or 'mean'
        pass
    return result.result_dict




#########################################################################3
ref_path = "incredibles.mp4"
dis_path = "incredibles_360p.mp4"
width    = 1280
height   = 720
fmt      = "yuv420p"
res_vmaf = run_vmaf(ref_path, dis_path, width, height, fmt)
res_psnr = run_psnr(ref_path, dis_path, width, height, fmt)