from flask import Flask, render_template, request
import characters

app = Flask(__name__)


@app.route('/')
def index():
    name = request.args.get('name')
    status = request.args.get('status')
    gender = request.args.get('gender')
    page = request.args.get('page')

    # если запроса от пользователя не поступило (т.е. все значения None или все значения заданы по умолчанию)
    if not (name or status or gender) or (not name and status == 'Status' and gender == 'Gender'):
        if characters.get_all_characters(page=page) is None:
            return page_not_found(page)

        pages, list_characters = characters.get_all_characters(page=page)

        return render_template('paginate_all.html', characters=list_characters, pages=pages)

    # обрабатываем запрос по форме
    if characters.get_filter_characters(page=page, name=name, status=status, gender=gender) is None:
        return page_not_found(page)

    pages, filter_characters = characters.get_filter_characters(page=page, name=name, status=status, gender=gender)

    return render_template('paginate_filter.html', characters=filter_characters, pages=pages, page=page)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/character/<id_>')
def character(id_):
    if not id_.isdigit() or not (1 <= int(id_) <= characters.count_characters):
        return page_not_found(id_)

    other, single_character = characters.get_single_character(id_=id_)

    return render_template('character.html', character=single_character, other=other)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()
