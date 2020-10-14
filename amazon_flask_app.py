

from flask import Flask, render_template, request,jsonify
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as ureq
import pymongo




app = Flask(__name__)
@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST':
        search = request.form['content'] # obtaining the search string entered in the form
        try:
            dbConn=pymongo.MongoClient("mongodb://localhost:27017/")
            db=dbConn['amazon_product']
            product = db[search].find({})#same as sql select statement
            if product.count()>0:
                return render_template('results.html',product=product)
            else:
                amazon_url="https://www.amazon.in/s?k=" + search
                uClient=ureq(amazon_url)
                page=uClient.read()
                uClient.close()

                amazon_html = bs(page, "html.parser")

                try:
                    bigbox_entry = amazon_html.findAll("a", {"class": "a-link-normal a-text-normal"})
                    del bigbox_entry[:2]
                    box = bigbox_entry[0]
                    name = bigbox_entry[0].span.text



                except:
                    name="no name"

                try:
                    entry_to_box = "https://www.amazon.in" + box['href']
                    page1= ureq(entry_to_box)
                    page_read = page1.read()
                    page1.close()

                    new_page = bs(page_read,"html.parser")
                    price=new_page.findAll("td",{"class":"a-span12"})
                    price=price[1].span.text
                    price=price[0]+price[2:]

                except:
                    price="no price"

                try:
                    rating = new_page.find("span",{"class":"a-icon-alt"})
                    rating = rating.text
                except:
                    rating = "no rating"
                try:
                    reviewer_name = new_page.findAll("span", {"class" : "a-profile-name"})
                    r_name = []
                    for i in range(2):
                        r_name.append(reviewer_name[i].text)
                except:
                    r_name.append("no name")

                try:
                    review = new_page.findAll("div",{"data-hook":"review"})
                    riv = []
                    for i in range(2):
                        index = review[i].text.find('Read more')
                        comment = review[i].text[0:index]
                        riv.append(comment)

                except:
                    riv.append("no review")

            #list=[]
                product = db[search] #creating table
                my_dict={"price":price,"name":name,"rating":rating,"r_name":r_name,"riv":riv}
                product.insert_one(my_dict)
                product = db[search].find()
                return render_template('results.html', product=product)
        except:
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=8000,debug=True)






