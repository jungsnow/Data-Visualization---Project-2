#!/bin/sh

ROOTPWD=${PWD}
cd backend/pipeline/

# KR 
python data_loading_db.py -c configs/master_kr.json
python team_composition_db.py -c configs/master_kr.json
python optimizer.py -c configs/config_xgb_kr_master.json


# NA1
python data_loading_db.py -c configs/master_na.json
python team_composition_db.py -c configs/master_na.json
python optimizer.py -c configs/config_xgb_master.json

# EUW1
python data_loading_db.py -c configs/master_euw.json
python team_composition_db.py -c configs/master_euw.json
python optimizer.py -c configs/config_xgb_euw_master.json