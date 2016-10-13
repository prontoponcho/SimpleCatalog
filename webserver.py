import cgi
import sys

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Base, Restaurant, MenuItem

# Connecting to database
session = None
db_name = 'sqlite:///restaurantmenu.db'
try:
    engine = create_engine(db_name)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
except:
    print "Error connecting to {}".format(db_name)

# HTML forms
html_base = "<html><body> %s </body></html>"
html_ul = "<ul style='list-style: none;'> %s </ul>"
html_li = """<li> <div> {name} </div>  
                <div><a href='/restaurants/{id}/edit'>edit</a> | 
                <a href='/restaurants/{id}/delete'>delete</a></div>
             </li>
             <br>
          """

class webserverHandler(BaseHTTPRequestHandler):

    # Convenience method
    def render_html(self, output):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_base % output)

    # Convenience method
    def redirect_to_front(self):
        self.send_response(302)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/restaurants')
        self.end_headers()  

    def do_GET(self):

        try:
            if self.path.endswith("/delete"):
                restaurant_id = int(self.path.split('/')[2])
                restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_id).first()

                output = ""
                if restaurant != []:
                    output = """<form method='POST' enctype='multipart/form-data' action='/restaurants/{id}/delete'>
                                    <h2>Delete {name} from the database?</h2>
                                    <input type='submit' value='Yes' name='response'>
                                    <input type='submit' value='No' name='response'>
                                </form>
                             """.format(id=restaurant_id, name=restaurant.name)
                else:
                    output = "Cannot continue the request"

                self.render_html(output)
                return  

            if self.path.endswith("/edit"):
                restaurant_id = int(self.path.split('/')[2])
                restaurant = session.query(Restaurant.name).filter(Restaurant.id==restaurant_id).first()

                output = ""
                if restaurant != []:
                    output += """<form method='POST' enctype='multipart/form-data' action='/restaurants/{id}/edit'>
                                    <h2>Add a new restaurant:</h2>
                                    <input name='content' type='text' value='{name}'>
                                    <input type='submit' value='Submit'>
                                 </form>
                              """.format(id=restaurant_id, name=restaurant.name)
                else:
                    output = "Cannot continue the request"

                self.render_html(output)
                return              

            if self.path.endswith("/restaurants"):
                output = "<div><a href='/restaurants/new'>Add New Restaurant</a><div><br>"
                restaurants = session.query(Restaurant).all()
                
                if restaurants != []:
                    for r in restaurants:
                        output += html_li.format(name=r.name, id=r.id)

                output = html_ul % output

                self.render_html(output)
                return

            if self.path.endswith("/restaurants/new"):
                output = """<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>
                             <h2>Add a new restaurant:</h2>
                             <input name='content' type='text'>
                             <input type='submit' value='Submit'>
                             </form>
                          """

                self.render_html(output)
                return

        except IOError:
            self.send_error(404, "File Not Found {}".format(self.path))

    def do_POST(self):

        try:
            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    response = fields.get('response')[0]

                    print "Response is {}".format(response)

                    if response == 'Yes':
                        restaurant_id = int(self.path.split('/')[2])
                        restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_id).first()
                        session.delete(restaurant)
                        session.commit()

                    self.redirect_to_front()
                    return

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    content = fields.get('content')[0]

                    print "Content is {}".format(content)

                    restaurant_id = int(self.path.split('/')[2])

                    print "Restaurant id is {}".format(restaurant_id)

                    restaurant = session.query(Restaurant).filter(Restaurant.id==restaurant_id).first()

                    if restaurant != []:
                        print "Restaurant name is {}".format(restaurant.name)
                        restaurant.name = content
                        session.add(restaurant)
                        session.commit()

                    self.redirect_to_front()
                    return

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    content = fields.get('content')[0]

                if content:
                    restaurant = Restaurant(name=content)
                    session.add(restaurant)
                    session.commit()

                self.redirect_to_front()
                return

        except:
            print "exception in POST"
            print("Unexpected error:", sys.exc_info()[0])

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port {}".format(port)
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        session.close()
        server.socket.close()

if __name__ == '__main__':
    main()