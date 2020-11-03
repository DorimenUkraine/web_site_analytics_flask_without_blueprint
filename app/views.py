import os
import base64
from datetime import datetime
from urllib.parse import urlparse
from urllib.parse import unquote
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

from loguru import logger  # удобный логгер ошибок - https://www.youtube.com/watch?v=3ndEeGDVqD4

from app import app
from app import geo
from flask import render_template, request, redirect, url_for, flash, make_response, Response, abort
from flask_login import login_required, login_user, current_user, logout_user
from flask_paginate import Pagination, get_page_parameter
from .models import Users, Sites, Visits, db
from .forms import SignIn, SignUp, SettingsForm
from .extensions import security
from werkzeug.security import generate_password_hash, check_password_hash

logger.add("logs/debug.json",
           format="{time} {level} {message}",
           level="DEBUG",
           rotation="10:00",
           compression="zip",
           serialize=True)

# cmb.js
with app.app_context():
    domain = urlparse('http://127.0.0.1:5000/').netloc
    cmbjs = render_template('cmb.js', domain=domain)
    # cmbjs = cmbjs.replace('\n', '').replace('  ', '')


@logger.catch
@app.route('/cmb.js')
def serve_cmbjs():
    """Serve cmb.js script."""
    response = Response(cmbjs, mimetype='text/javascript')
    response.cache_control.max_age = 900  # 15 minutes

    return response


# one pixel gif
val = 'R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='
one_pxl = base64.b64decode(val)


@logger.catch
@app.route('/<int:gif_id>.gif')
def parse_query_string(gif_id):
    """Parse gif query string and store in db."""
    if not request.args.get('cid'):
        abort(404)

    query_type = request.args.get('t')
    ip = security.real_ip(request, app.config.get('PROXY_COUNT', 0))

    # сделаю небольшую проверку данные, которые передает установленный на сайте скрипт, а именно:
    # если урл, с которого нам передают данные, не находится в нашей базе данных сайтов клиентов,
    # то данные от js-скрипта не принимаем.

    client_domain = urlparse(request.args.get('dl')).netloc

    total_sites = Sites.query.filter(Sites.url.contains(client_domain)).first_or_404()

    if total_sites.url:

        if query_type == 'visit':
            geo_data = geo.query(ip)
            data = dict(ip=ip,
                        cid=request.args.get('cid'),
                        session=request.args.get('session'),
                        datetime=datetime.utcnow(),
                        doc_title=unquote(request.args.get('dt')),
                        doc_uri=unquote(request.args.get('dl')),
                        doc_enc=request.args.get('de'),
                        referrer=unquote(request.args.get('dr')),
                        _referrer=getattr(request, 'referrer', None),
                        platform=getattr(request.user_agent, 'platform', None),
                        browser=getattr(request.user_agent, 'browser', None),
                        version=getattr(request.user_agent, 'version', None),
                        screen_res=request.args.get('sr'),
                        screen_depth=request.args.get('sd'),
                        continent=geo_data.get('continent', None),
                        country=geo_data.get('country', None),
                        subdivision_1=geo_data.get('subdivision_1', None),
                        subdivision_2=geo_data.get('subdivision_2', None),
                        city=geo_data.get('city', None),
                        latitude=geo_data.get('latitude', None),
                        longitude=geo_data.get('longitude', None),
                        accuracy_radius=geo_data.get('accuracy_radius', None),
                        time_zone=geo_data.get('time_zone', None),
                        lang=request.args.get('ul'),
                        _lang=getattr(request.user_agent, 'language', None), )
            # logger.debug(data)
            db.session.add(Visits(**data))
            db.session.commit()
        elif query_type == 'event':
            geo_data = geo.query(ip)
            data = dict(ip=ip,
                        cid=request.args.get('cid'),
                        session=request.args.get('session'),
                        datetime=datetime.utcnow(),
                        doc_title=unquote(request.args.get('dt')),
                        doc_uri=unquote(request.args.get('dl')),
                        doc_enc=request.args.get('de'),
                        referrer=unquote(request.args.get('dr')),
                        _referrer=getattr(request, 'referrer', None),
                        platform=getattr(request.user_agent, 'platform', None),
                        browser=getattr(request.user_agent, 'browser', None),
                        version=getattr(request.user_agent, 'version', None),
                        screen_res=request.args.get('sr'),
                        screen_depth=request.args.get('sd'),
                        continent=geo_data.get('continent', None),
                        country=geo_data.get('country', None),
                        subdivision_1=geo_data.get('subdivision_1', None),
                        subdivision_2=geo_data.get('subdivision_2', None),
                        city=geo_data.get('city', None),
                        latitude=geo_data.get('latitude', None),
                        longitude=geo_data.get('longitude', None),
                        accuracy_radius=geo_data.get('accuracy_radius', None),
                        time_zone=geo_data.get('time_zone', None),
                        lang=request.args.get('ul'),
                        _lang=getattr(request.user_agent, 'language', None),
                        name=request.args.get('en'),
                        value=request.args.get('ev'),
                        target=True, )
            # logger.debug(data)
            db.session.add(Visits(**data))
            db.session.commit()
        else:
            print('Invalid request type: {}'.format(query_type))

    return Response(one_pxl, mimetype='image/gif')


@logger.catch
@app.route("/index", methods=['POST', 'GET'])
@app.route("/", methods=['POST', 'GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('account'))

    form = SignIn()
    if form.validate_on_submit():
        user = db.session.query(Users). \
            filter(Users.email == form.email.data). \
            first()
        if user and user.check_password(form.psw.data):
            login_user(user, remember=form.remember.data)
            return redirect(request.args.get('next') or url_for('account'))

        flash('Invalid login or password', 'error')

    return render_template('index.html', title='Authorization', form=form)


@logger.catch
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='Page not found / Web Site Tools Analytics Platform'), 404


@logger.catch
@app.route("/account")
@login_required
def account(chartID='chart_ID', chart_type='line', chart_height=350):
    # объявляю id авторизированного пользователя через специальный метод current_user
    user_id = current_user.id

    # достану из БД данные по сессиям сайта, которые добавил данный пользователь
    # пока у пользователя есть ограничение - он может добавтиь только один сайт
    # но на всякий случай перестрахуюсь и вытащу первый
    current_user_sites = db.session.query(Sites). \
        filter(Sites.user_id == user_id). \
        first()

    # теперь найду все данные по сайту по событиям на сайте, который получил выше
    total_search_data = db.session.query(Visits). \
        filter(Visits.doc_uri.contains(current_user_sites.url)). \
        order_by(Visits.datetime.desc())

    # данные для построения графика - дата, cid, target
    df_datetime = [datetime.strptime(f'{row.datetime.year}:{row.datetime.month}:{row.datetime.day}:{row.datetime.hour}',
                                     '%Y:%m:%d:%H') for row in total_search_data.all()]
    df_cid = [row.cid for row in total_search_data.all()]
    df_sesssion = [row.session for row in total_search_data.all()]
    df_target = [row.target for row in total_search_data.all()]

    # создам датафрейм
    df = pd.DataFrame(list(zip(df_datetime, df_cid, df_sesssion, df_target)), columns=['datetime', 'cid', 'session', 'target'])

    # сгруппирую по дате и времени - просуммирую сколько было сессий
    df_datetime_session_count = df.groupby('datetime') \
        .agg({'session': 'count'}) \
        .sort_values(by=['datetime'], ascending=True) \
        .reset_index()

    list_datetime_from_df_datetime = df_datetime_session_count['datetime'].astype(str).tolist()
    list_cid_from_df_datetime_session_count = df_datetime_session_count['session'].tolist()

    # сгруппирую по дате и времени - просуммирую количество уникальных сессий
    df_datetime_cid_nunique = df.groupby('datetime') \
        .agg({'cid': 'nunique'}) \
        .sort_values(by=['datetime'], ascending=True) \
        .reset_index()

    list_cid_from_df_datetime_cid_nunique = df_datetime_cid_nunique['cid'].tolist()

    # сгруппирую по дате и времени - просуммирую количество целевых действий
    df_datetime_target_nunique = df[df['target'] == True] \
        .groupby('datetime') \
        .agg({'target': 'count'}) \
        .sort_values(by=['datetime'], ascending=True) \
        .reset_index()

    list_target_from_df_datetime_target_count = df_datetime_target_nunique['target'].tolist()

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height, }
    series = [{"name": 'Sessions per hour', "data": list_cid_from_df_datetime_session_count},
              {"name": 'Unique users per hour', "data": list_cid_from_df_datetime_cid_nunique},
              {"name": 'Targets per hour', "data": list_target_from_df_datetime_target_count}]
    xAxis = {"categories": list_datetime_from_df_datetime}
    yAxis = {"title": {"text": 'Counts'}}

    # сделаем пагинацию по найденным данным для табличного отображения
    # количество элементов на странице
    POSTS_PER_PAGE = 10

    # параметры для нумерации страниц, page внутри скобок - это приставка в урле
    page = request.args.get('page', 1, type=int)

    # а теперь сформирую данные, которые я вытащил по данному сайту, и загоню их в пагинатор для отображения в таблице
    table_data_paginations = total_search_data.paginate(page, POSTS_PER_PAGE, False)

    # ну а это у меня параметры для перехода назад и вперед по пагинатору
    next_url = url_for('account', page=table_data_paginations.next_num) \
        if table_data_paginations.has_next else None
    prev_url = url_for('account', page=table_data_paginations.prev_num) \
        if table_data_paginations.has_prev else None
    total_items = table_data_paginations.total

    # приводим индексы к стандарту pd.Datetime, чтобы потом это можно было скормить seasonal_decompose
    df_seasons = df.set_index(pd.DatetimeIndex(df['datetime']))
    # замечаем, что т.к. у нас теперь есть индекс Month, нам больше не нужен столбец Month, который его дублирует
    df_seasons.drop(['datetime'], axis=1, inplace=True)
    # print(df_seasons)
    # применяем seasonal_decompose
    # эта функция разложит ряд на трендовую, сезонную и шумовую составляющие
    # decomposition = seasonal_decompose(df_seasons, model='additive')
    # decomposition.plot()

    return render_template('account.html',
                           title='Account / Web Site Tools Analytics Platform',
                           table_data=table_data_paginations,
                           next_url=next_url,
                           prev_url=prev_url,
                           total_items=total_items,
                           chartID=chartID,
                           chart=chart,
                           series=series,
                           xAxis=xAxis,
                           yAxis=yAxis)


@logger.catch
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are signed out', 'success')
    return redirect(url_for('index'))


@logger.catch
@app.route("/signup", methods=("POST", "GET"))
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('account'))

    form = SignUp()
    if form.validate_on_submit():
        email = form.email.data
        psw = form.psw.data

        try:
            hash = generate_password_hash(psw)
            user = Users(email=email, psw=hash)
            db.session.add(user)
            # из сессии перемещает записи в таблицу, но еще не записывает в саму таблицу
            db.session.flush()

            s = Sites(user_id=user.id)
            db.session.add(s)
            # идет физическая запись в БД
            db.session.commit()

            flash('Congratulations on your registration! Now you can log in to the system.', 'success')

            return redirect(url_for('index'))

        except:
            # если при добавлении в БД были какие-то ошибки, тогда откатываем БД до состояния, как будто ничего не записывали
            db.session.rollback()

            flash('Something went wrong. Please try again!', 'error')

            return redirect(url_for('signup'))

    return render_template("signup.html", title="Registration", form=form)


@logger.catch
@app.route("/settings", methods=['POST', 'GET'])
@login_required
def settings():
    user_id = current_user.id
    form = SettingsForm()
    if form.validate_on_submit():
        url = form.url.data

        is_site = db.session.query(Sites). \
            filter(Sites.user_id == user_id). \
            first()

        if is_site:
            try:
                db.session.query(Sites). \
                    filter(Sites.user_id == user_id). \
                    update({Sites.url: url})
                # идет физическая запись в БД
                db.session.commit()

                flash('Settings were successfully re-saved!', 'success')

                return redirect(url_for('settings'))

            except:

                # если при добавлении в БД были какие-то ошибки, тогда откатываем БД до состояния, как будто ничего не записывали
                db.session.rollback()

                flash('Failed to update site. Please try again!', 'error')

                return redirect(url_for('settings'))

        else:
            site = Sites(user_id=user_id, url=url)

            try:
                db.session.add(site)
                # идет физическая запись в БД
                db.session.commit()

                flash('Settings were successfully saved!', 'success')

                return redirect(url_for('settings'))

            except:
                # если при добавлении в БД были какие-то ошибки, тогда откатываем БД до состояния, как будто ничего не записывали
                db.session.rollback()

                flash('Failed to add site. Please try again!', 'error')

                return redirect(url_for('settings'))

    return render_template("settings.html", title="Settings", form=form)


@logger.catch
@app.route('/cookie')
def cookie():
    if not request.cookies.get('foo'):
        res = make_response("Setting a cookie")
        res.set_cookie('foo', 'bar', max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response("Value of cookie foo is {}".format(request.cookies.get('foo')))
    return res


@logger.catch
@app.route('/delete-cookie')
def delete_cookie():
    res = make_response("Cookie Removed")
    res.set_cookie('foo', 'bar', max_age=0)
    return res
