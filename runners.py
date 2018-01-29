from functools import partial
import sys
import os

import numpy as np

from vmaf.config import VmafConfig, DisplayConfig
from vmaf.core.asset import Asset
from vmaf.core.quality_runner import VmafQualityRunner,         \
                                     PsnrQualityRunner,         \
                                     VmafPhoneQualityRunner,    \
                                     SsimQualityRunner,         \
                                     MsSsimQualityRunner
from vmaf.tools.misc import get_file_name_without_extension,    \
                            get_cmd_option,                     \
                            cmd_option_exists
from vmaf.tools.stats import ListStats

FMTS = ['yuv420p', 'yuv422p', 'yuv444p', 'yuv420p10le', 'yuv422p10le', 'yuv444p10le']
POOL_METHODS = ['mean', 'harmonic_mean', 'min', 'median', 'perc5', 'perc10', 'perc20']

def run_helper(quality_runner_class):
    def f(ref_path, dis_path, width, height, fmt, pool_method=None):
        if fmt not in  FMTS:
            print("{} format is not supported. Supported formats: {}".format(fmt, FMTS))
            return

        asset = Asset(dataset="cmd",
                      content_id=abs(hash(get_file_name_without_extension(ref_path))) % (10 ** 16),
                      asset_id=abs(hash(get_file_name_without_extension(ref_path))) % (10 ** 16),
                      workdir_root=VmafConfig.workdir_path(),
                      ref_path=ref_path,
                      dis_path=dis_path,
                      asset_dict={'width':width, 'height':height, 'yuv_type':fmt}
                      )
        assets = [asset]

        runner_class = quality_runner_class
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
    return f


def run_vmaf(ref_path, dis_path, width, height, fmt, pool_method=None):
    fn = run_helper(VmafQualityRunner)
    return fn(ref_path, dis_path, width, height, fmt, pool_method=None)

def run_vmaf_phone(ref_path, dis_path, width, height, fmt, pool_method=None):
    fn = run_helper(VmafPhoneQualityRunner)
    return fn(ref_path, dis_path, width, height, fmt, pool_method=None)

def run_ssim(ref_path, dis_path, width, height, fmt, pool_method=None):
    fn = run_helper(SsimQualityRunner)
    return fn(ref_path, dis_path, width, height, fmt, pool_method=None)

def run_ms_ssim(ref_path, dis_path, width, height, fmt, pool_method=None):
    fn = run_helper(MsSsimQualityRunner)
    return fn(ref_path, dis_path, width, height, fmt, pool_method=None)

def run_psnr(ref_path, dis_path, width, height, fmt, pool_method=None):
    fn = run_helper(PsnrQualityRunner)
    return fn(ref_path, dis_path, width, height, fmt, pool_method=None)

def run_all(ref_path, dis_path, width, height, fmt, pool_method=None):
    return {'vmaf': run_vmaf(ref_path, dis_path, width, height, fmt),
            'psnr': run_psnr(ref_path, dis_path, width, height, fmt),
            'vmaf_phone': run_vmaf_phone(ref_path, dis_path, width, height, fmt),
            'ssim': run_ssim(ref_path, dis_path, width, height, fmt),
            'ms_ssim': run_ms_ssim(ref_path, dis_path, width, height, fmt)
            }

"""
ref_path: an 720p video file
dis_path: same video file in 360p
width:    1280
height:   720
fmt:      yuv420p

Example of run_all() output:

{'ms_ssim': {'MS_SSIM_feature_ms_ssim_c_scale0_scores': [0.989665],
  'MS_SSIM_feature_ms_ssim_c_scale1_scores': [0.98371],
  'MS_SSIM_feature_ms_ssim_c_scale2_scores': [0.976536],
  'MS_SSIM_feature_ms_ssim_c_scale3_scores': [0.977248],
  'MS_SSIM_feature_ms_ssim_c_scale4_scores': [0.986451],
  'MS_SSIM_feature_ms_ssim_l_scale0_scores': [0.970711],
  'MS_SSIM_feature_ms_ssim_l_scale1_scores': [0.985647],
  'MS_SSIM_feature_ms_ssim_l_scale2_scores': [0.997019],
  'MS_SSIM_feature_ms_ssim_l_scale3_scores': [0.999603],
  'MS_SSIM_feature_ms_ssim_l_scale4_scores': [0.999866],
  'MS_SSIM_feature_ms_ssim_s_scale0_scores': [0.005575],
  'MS_SSIM_feature_ms_ssim_s_scale1_scores': [0.019021],
  'MS_SSIM_feature_ms_ssim_s_scale2_scores': [0.076156],
  'MS_SSIM_feature_ms_ssim_s_scale3_scores': [0.242416],
  'MS_SSIM_feature_ms_ssim_s_scale4_scores': [0.544247],
  'MS_SSIM_scores': [0.076355]},
 'psnr': {'PSNR_scores': [7.55763]},
 'ssim': {'SSIM_feature_ssim_c_scores': [0.980021],
  'SSIM_feature_ssim_l_scores': [0.992573],
  'SSIM_feature_ssim_s_scores': [0.046105],
  'SSIM_scores': [0.04498]},
 'vmaf': {'VMAF_feature_adm2_scores': [0.38859511610567665],
  'VMAF_feature_motion2_scores': [0.0],
  'VMAF_feature_vif_scale0_scores': [0.0004596111501679125],
  'VMAF_feature_vif_scale1_scores': [0.011596009598797996],
  'VMAF_feature_vif_scale2_scores': [0.021518423990864594],
  'VMAF_feature_vif_scale3_scores': [0.04131660876342576],
  'VMAF_scores': array([7.9006446])},
 'vmaf_phone': {'VMAF_Phone_scores': array([14.90647078]),
  'VMAF_feature_adm2_scores': [0.38859511610567665],
  'VMAF_feature_motion2_scores': [0.0],
  'VMAF_feature_vif_scale0_scores': [0.0004596111501679125],
  'VMAF_feature_vif_scale1_scores': [0.011596009598797996],
  'VMAF_feature_vif_scale2_scores': [0.021518423990864594],
  'VMAF_feature_vif_scale3_scores': [0.04131660876342576]}}
"""
