import os
import sqlite3

# Ruta a la base de datos según settings: proyecto/ db.sqlite3
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'db.sqlite3')

print('Usando DB:', DB_PATH)
if not os.path.exists(DB_PATH):
    raise SystemExit('Base de datos no encontrada en ruta esperada')

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA foreign_keys = ON')
cur = conn.cursor()

def get_or_create_user(username, encrypted_password, session_token):
    cur.execute('SELECT id FROM rest_api_filmboxuser WHERE username = ?', (username,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute('INSERT INTO rest_api_filmboxuser (username, encrypted_password, session_token) VALUES (?, ?, ?)',
                (username, encrypted_password, session_token))
    conn.commit()
    return cur.lastrowid

def get_or_create_category(title, image_url):
    cur.execute('SELECT id FROM rest_api_category WHERE title = ?', (title,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute('INSERT INTO rest_api_category (title, image_url) VALUES (?, ?)', (title, image_url))
    conn.commit()
    return cur.lastrowid

def get_or_create_film(title, description, image_url, film_url, trailer_url, year, length, director):
    cur.execute('SELECT id FROM rest_api_film WHERE title = ? AND year = ?', (title, year))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute('''INSERT INTO rest_api_film (title, description, image_url, film_url, trailer_url, year, length, director)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (title, description, image_url, film_url, trailer_url, year, length, director))
    conn.commit()
    return cur.lastrowid

def add_category_film(category_id, film_id):
    cur.execute('SELECT id FROM rest_api_categoryfilm WHERE category_id = ? AND film_id = ?', (category_id, film_id))
    if cur.fetchone():
        return
    cur.execute('INSERT INTO rest_api_categoryfilm (category_id, film_id) VALUES (?, ?)', (category_id, film_id))
    conn.commit()

def add_relation(table, user_id, film_id):
    # table in ('rest_api_favoritefilm','rest_api_wishlistfilm','rest_api_watchedfilm')
    cur.execute(f'SELECT id FROM {table} WHERE user_id = ? AND film_id = ?', (user_id, film_id))
    if cur.fetchone():
        return
    cur.execute(f'INSERT INTO {table} (user_id, film_id) VALUES (?, ?)', (user_id, film_id))
    conn.commit()

def add_comment(user_id, film_id, content, score):
    cur.execute('SELECT id FROM rest_api_comment WHERE user_id = ? AND film_id = ?', (user_id, film_id))
    if cur.fetchone():
        return
    cur.execute('INSERT INTO rest_api_comment (user_id, film_id, content, score) VALUES (?, ?, ?, ?)',
                (user_id, film_id, content, score))
    conn.commit()

# Datos a insertar
u1 = get_or_create_user('alice', 'pass123', 'token-alice-0001')
u2 = get_or_create_user('bob', 'secret', 'token-bob-0001')

c_accion = get_or_create_category('Acción', 'https://example.com/accion.jpg')
c_aventura = get_or_create_category('Aventura', 'https://example.com/aventura.jpg')
c_ciencia = get_or_create_category('Ciencia ficción', 'https://example.com/ciencia.jpg')
c_drama = get_or_create_category('Drama', 'https://example.com/drama.jpg')

f_avatar = get_or_create_film('Avatar', 'Un ex-marine en Pandora...', 'https://example.com/avatar.jpg',
                              'https://example.com/see-avatar', 'https://example.com/avatar-trailer', 2009, 162, 'James Cameron')

f_inception = get_or_create_film('Inception', 'Un ladrón que roba secretos a través de los sueños...',
                                 'https://example.com/inception.jpg', 'https://example.com/see-inception',
                                 'https://example.com/inception-trailer', 2010, 148, 'Christopher Nolan')

# Asociar categorías
add_category_film(c_accion, f_avatar)
add_category_film(c_ciencia, f_avatar)
add_category_film(c_accion, f_inception)
add_category_film(c_aventura, f_inception)
add_category_film(c_ciencia, f_inception)

# Favoritos / wishlist / vistos
add_relation('rest_api_favoritefilm', u1, f_avatar)
add_relation('rest_api_wishlistfilm', u1, f_inception)
add_relation('rest_api_watchedfilm', u2, f_avatar)

# Comentarios
add_comment(u1, f_avatar, '¡Me encantó!', 5)
add_comment(u2, f_inception, 'Muy interesante', 4)

# Resumen
print('Usuarios:', cur.execute('SELECT id, username FROM rest_api_filmboxuser').fetchall())
print('Categorias:', cur.execute('SELECT id, title FROM rest_api_category').fetchall())
print('Peliculas:', cur.execute('SELECT id, title, year FROM rest_api_film').fetchall())
print('CategoryFilm:', cur.execute('SELECT id, category_id, film_id FROM rest_api_categoryfilm').fetchall())
print('FavoriteFilm:', cur.execute('SELECT id, user_id, film_id FROM rest_api_favoritefilm').fetchall())
print('WishlistFilm:', cur.execute('SELECT id, user_id, film_id FROM rest_api_wishlistfilm').fetchall())
print('WatchedFilm:', cur.execute('SELECT id, user_id, film_id FROM rest_api_watchedfilm').fetchall())
print('Comments:', cur.execute('SELECT id, user_id, film_id, content, score FROM rest_api_comment').fetchall())

conn.close()
print('Hecho')

