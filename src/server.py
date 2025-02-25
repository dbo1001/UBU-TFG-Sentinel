from flask import Flask, jsonify, redirect, url_for, request
from flask_cors import CORS
import mysql.connector
import os
import json
from instagram import *
from twitter import *
from database import *
from time_series import *
app = Flask(__name__)
CORS(app)



@app.route('/login', methods=['POST'])
def login():
    result = get_user(request.json)
    return jsonify({'resultado': result})

@app.route('/register', methods=['POST'])
def register_db():
    register_users(request.json)
    return jsonify({'ok': True})

@app.route('/')
def titulo():

    return jsonify({'text': 'Hola!!!'})

@app.route('/idTwitterInDB', methods=['GET'])
def checkIdInDBTw():
    result = checkIdinDBTw(request.args.get('id'))
    return jsonify({'id': result})

@app.route('/searchTwitter', methods=['GET'])
def searchIdTw():
    if request.args.get('id')[0] == '#':
        searchHashtag(request.args.get('id'))
    elif request.args.get('id')[0] == '@':
        searchUser(request.args.get('id'))
    else:
        searchWord(request.args.get('id'))

    return jsonify({'ok': True})

@app.route('/idInstagramInDB', methods=['GET'])
def checkIdInDBIg():
    result = checkIdInDBIG(request.args.get('id'))
    return jsonify({'id': result})

@app.route('/searchInstagram', methods=['GET'])
def searchIdIg():
    api_ig = main()
    userId = search_users(api_ig, request.args.get('id'))
    if userId != False:
        getMediaData(api_ig, userId, request.args.get('id'))
    else:
        return jsonify({'userExists': False})
    return jsonify({'userExists': True})

@app.route('/getDataforDashboard', methods=['GET'])
def getDataforDashboard():

    if request.args.get('is_tw') == 'true':
        if request.args.get('id')[0] == '#':
            analysis_score = select_dataHashtags(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))
        elif request.args.get('id')[0] == '@':
            analysis_score = select_dataUserTw(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))
        else:
            analysis_score = select_dataWord(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))
    else:
        analysis_score = select_dataUserIg(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))


    return jsonify({'data':analysis_score})

@app.route('/getDataforGraphs', methods=['GET'])
def getDataforGraphs():

    if request.args.get('is_tw') == 'true':
        if request.args.get('id')[0] == '#':
            analysis_score = selectHashtagsGroupByDates(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))
        elif request.args.get('id')[0] == '@':
            analysis_score = selectUserTwGroupByDates(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))
        else:
            analysis_score = selectWordGroupByDates(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))
    else:
        analysis_score = selectDataUserIgByDates(request.args.get('id'), request.args.get('since_date'), request.args.get('until_date'))


    return jsonify({'data':analysis_score})

@app.route('/intervalGraph', methods=['GET'])
def getDataForIntervalGraph():
    if request.args.get('is_tw') == 'true':
        if request.args.get('id')[0] == '#':
            if request.args.get('is_dynamic') == 'true':
                analysis_score = selectHashtagsByIntervals(request.args.get('id'), request.args.get('since_date'),
                                                           request.args.get('until_date'))
            else:
                analysis_score = selectHashtagsByFixedIntervals(request.args.get('id'), request.args.get('since_date'),
                                                                request.args.get('until_date'))
        elif request.args.get('id')[0] == '@':
            if request.args.get('is_dynamic') == 'true':
                analysis_score = selectUserTwByIntervals(request.args.get('id'), request.args.get('since_date'),
                                                           request.args.get('until_date'))
            else:
                analysis_score = selectUserTwByFixedIntervals(request.args.get('id'), request.args.get('since_date'),
                                                                request.args.get('until_date'))
        else:
            if request.args.get('is_dynamic') == 'true':
                analysis_score = selectWordByIntervals(request.args.get('id'), request.args.get('since_date'),
                                                           request.args.get('until_date'))
            else:
                analysis_score = selectWordByFixedIntervals(request.args.get('id'), request.args.get('since_date'),
                                                                request.args.get('until_date'))
    else:
        if request.args.get('is_dynamic') == 'true':
            analysis_score = selectDataUserIgByIntervals(request.args.get('id'), request.args.get('since_date'),
                                                         request.args.get('until_date'))
        else:
            analysis_score = selectDataUserIgByFixedIntervals(request.args.get('id'), request.args.get('since_date'),
                                                         request.args.get('until_date'))


    return jsonify({'data':analysis_score})

@app.route('/pieChart', methods=['GET'])
def getDataForPieChart():
    if request.args.get('is_tw') == 'true':
        if request.args.get('id')[0] == '#':
            analysis_score = selectHashtagsForPieChart(request.args.get('id'), request.args.get('since_date'),
                                                           request.args.get('until_date'))
        elif request.args.get('id')[0] == '@':
            analysis_score = selectUserTwForPieChart(request.args.get('id'), request.args.get('since_date'),
                                                      request.args.get('until_date'))
        else:
            analysis_score = selectWordForPieChart(request.args.get('id'), request.args.get('since_date'),
                                                    request.args.get('until_date'))
    else:
        analysis_score = selectDataUserIgForPieChart(request.args.get('id'), request.args.get('since_date'),
                                                 request.args.get('until_date'))

    return jsonify({'data':analysis_score})

@app.route('/statistics', methods=['GET'])
def getStatisticsForTable():
    statistics = select_statistics(request.args.get('id'))

    return jsonify({'data':statistics})

@app.route('/timeSerie', methods=['GET'])
def getTimeSeries():
    obj_data,obj_data_time_serie,proyeccion,estacionaria, estacionalidad, tendencia, residuo = loading_data(request.args.get('id'),
                                        request.args.get('since_date'), request.args.get('until_date'),
                                        request.args.get('is_tw'),request.args.get('type'), request.args.get('schema'),
                                        request.args.get('num_periods'))


    return jsonify(data_original = obj_data, data_time_serie = obj_data_time_serie, proyeccion = proyeccion, estacionaria = estacionaria,
                   estacionalidad = estacionalidad, tendencia = tendencia, residuo = residuo)

if __name__ == '__main__':
    app.run()

