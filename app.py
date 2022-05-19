from flask import Flask, jsonify
import sqlite3


def main():
    app = Flask(__name__)
    app.config['JSON_AS_ASCII'] = False
    app.config['DEBUG'] = True

    def connect_netflix(query):
        with sqlite3.connect('netflix.db') as connection:
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
        return result

    @app.route('/movie/<title>')
    def get_query_by_title(title):
        query = f"""
                SELECT 
                    title, 
                    country, 
                    release_year,
                    listed_in AS genre,
                    description
                FROM netflix
                WHERE title = '{title}'
                ORDER BY release_year DESC
                LIMIT 1
        """
        response = connect_netflix(query)[0]
        if len(response) == 0:
            response_json = {}
        else:
            response_json = {
                'title': response[0],
                'country': response[1],
                'release_year': response[2],
                'genre': response[3],
                'description': response[4].strip(),
            }
        return jsonify(response_json)

    @app.route('/movie/<int:start>/to/<int:end>')
    def get_query_by_year(start, end):
        query = f"""
                SELECT 
                    title, 
                    release_year
                FROM netflix
                WHERE release_year BETWEEN {start} AND {end}
                ORDER BY release_year
                LIMIT 100
        """
        response = connect_netflix(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'release_year': film[1]
            })
        return jsonify(response_json)

    @app.route('/rating/<group>')
    def get_query_by_rating(group):
        params = {
            'children': ['G'],
            'family': ['G', 'PG', 'PG-13'],
            'adult': ['R', 'NC-17']
        }
        if group in params:
            param = '\", \"'.join(params[group])
            param = f'\"{param}\"'
        else:
            return jsonify([])
        query = f"""
                SELECT 
                    title, 
                    rating,
                    description
                FROM netflix
                WHERE rating IN ({param})
        """
        response = connect_netflix(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'rating': film[1],
                'description': film[2].strip()
            })
        return jsonify(response_json)

    @app.route('/genre/<genre>')
    def get_query_by_genre(genre):
        query = f"""
                SELECT 
                    title, 
                    description
                FROM netflix
                WHERE listed_in LIKE '%{genre}%'
                ORDER BY release_year DESC
                LIMIT 10
        """
        response = connect_netflix(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'description': film[1].strip()
            })
        return jsonify(response_json)

    def get_actors_list(name1, name2):
        query = f"""
                SELECT 
                    "cast"
                FROM netflix
                WHERE "cast" LIKE '%{name1}%'
                AND "cast" LIKE '%{name2}%'
        """
        response = connect_netflix(query)
        get_list = []
        for cast in response:
            get_list.extend(cast[0].split(', '))
        result = []
        for name in get_list:
            if name not in [name1, name2]:
                if get_list.count(name) > 2:
                    result.append(name)
        result = set(result)
        return result
    print(get_actors_list(name1='Rose McIver', name2='Ben Lamb'))

    def get_films(type_, release_year, genre):
        query = f"""
                SELECT 
                    title,
                    description
                FROM netflix
                WHERE "type" = '{type_}'
                    AND release_year = '{release_year}'
                    AND listed_in LIKE '{genre}'
        """
        response = connect_netflix(query)
        response_json = []
        for film in response:
            response_json.append({
                'title': film[0],
                'description': film[1]
            })
        return response_json
    print(get_films(type_='Movie', release_year=2016, genre='Dramas'))

    app.run()


if __name__ == '__main__':
    main()
