import os
from flask import Flask, render_template, request, redirect, jsonify
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '86d119405b0d0a506506f0ei963ce914'
socketio = SocketIO(app)

def load_photos():
  with open('photos.json') as f:
    data = json.load(f)
  return data['photos']

def upvote_photo(photo_id):
  with open('photos.json') as f:
    data = json.load(f)

  for photo in data['photos']:
    if photo['id'] == photo_id:
      photo['votes'] += 1
      socketio.emit('vote_update', photo, broadcast=True)
      break

  with open('photos.json', 'w') as f:
    json.dump(data, f)

@app.route('/')
def display_gallery():
  photos = load_photos()
  sorted_photos = sorted(photos, key=lambda x: x['votes'], reverse=True)
  return render_template('index.html', photos=sorted_photos)

@app.route('/upvote', methods=['POST'])
def handle_upvote():
  photo_id = request.form['photo_id']
  photo_id = int(photo_id)
  upvote_photo(photo_id)
  photos = load_photos()
  socketio.emit('vote_update', photos, broadcast=True)

  return jsonify(photos)

@socketio.on('connect')
def handle_connect():
  photos = load_photos()
  emit('load_photos', photos)

@socketio.on('update_photo')
def update_photo():
  print('updating photos')
  photos = load_photos()
  emit('load_photos', photos)
  
def write_to_json(photo_id,photo_votes):
  with open('photos.json') as f:
    data = json.load(f)
  for photo in data['photos']:
    if photo['id'] == photo_id:
      photo['votes'] = photo_votes
      break
  with open('photos.json', 'w') as f:
    json.dump(data, f)
  


@socketio.on('vote_update')
def handle_vote_update(photo_data):
  photo_id = photo_data['id']
  photo_votes = photo_data['votes']
  photo_votes=int(photo_votes)+1
  write_to_json(photo_id,photo_votes)
  # script = f"document.querySelector('#photo-{photo_id} .vote-count').textContent = '{photo_votes}';"
  script={
    'id': photo_id,
    'votes': photo_votes
  }
  emit('update_vote', script, broadcast=True)
 

if __name__ == '__main__':
  app.run(debug=True)
  socketio.run(app, host='192.168.1.100', port=int(os.environ.get('PORT', 5000)))
