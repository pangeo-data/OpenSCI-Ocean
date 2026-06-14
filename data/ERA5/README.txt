ERA5 数据下载步骤
=================

1. 注册 CDS 账号:
   https://cds.climate.copernicus.eu/user/register

2. 获取 API key 保存到 ~/.cdsapirc:
   url: https://cds.climate.copernicus.eu/api/v2
   key: <UID>:<API-key>

3. 安装 cdsapi:
   pip install cdsapi

4. 运行下载脚本:
   python dl_era5_wind.py
