#!/bin/sh

ROOTPWD=${PWD}
cd backend/pipeline/

# KR 
python data_loading_db.py -c configs/grandmasters_kr.json
python team_composition_db.py -c configs/grandmasters_kr.json
python optimizer.py -c configs/config_xgb_kr_grandmaster.json


# NA1
python data_loading_db.py -c configs/grandmasters_na.json
python team_composition_db.py -c configs/grandmasters_na.json
python optimizer.py -c configs/config_xgb_grandmaster.json

# EUW1
python data_loading_db.py -c configs/grandmasters_euw.json
python team_composition_db.py -c configs/grandmasters_euw.json
python optimizer.py -c configs/config_xgb_euw_grandmaster.json