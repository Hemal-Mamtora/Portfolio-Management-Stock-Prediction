from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.conf import settings
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import generics
from .models import User, Stocks, Transaction
import os
import numpy as np
import pickle
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

#from googlefinance.client import get_price_data, get_prices_data, get_prices_time_data

future = []




def scaling(X_train):
  X_train = X_train.reshape(-1, 1)
  sc = MinMaxScaler(feature_range = (0, 1))
  training_set_scaled = sc.fit_transform(X_train)
  return training_set_scaled, sc

def load_model(filename):
  reg = pickle.load(open(filename, 'rb'))
  return reg

def test_sol(X, sc, regressor):
  #X_t = X_test.reshape((-1, 1))
  #print(X_t.shape)
  var = X.reshape((-1, 1))
  #print(var.shape)
  #np.concatenate((X_train, X_test.reshape(-1, 1)), axis = 0) 
  inputs = sc.transform(var)

  X_test = []
  #print(inputs.shape)
  for i in range(60, inputs.shape[0]):
    X_test.append(inputs[i-60:i, 0])
  
  X_test = np.array(X_test)
  #print("X_test.shape ", X_test.shape)
  #X_test.shape
  X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
  #print(X_test)
  #for i in range(0, 60):
  #  print(X_test[0][i], X_test[1][i])
  predicted_stock_price = regressor.predict(X_test)
  predicted_stock_price = sc.inverse_transform(predicted_stock_price)

  return predicted_stock_price #X is real stock prices
# %matplotlib inline

def perpetual(count, X, sc, regressor):
  '''
  X should be shaped as 1, 60, 1
  '''
  for i in range(count):
    #print(X)
    #var = X_test = X.reshape((-1, 1)) #60, 1
    inputs = sc.transform(X)
    X_test = np.array(inputs)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    #print("predicted: ", predicted_stock_price)
    future.append(predicted_stock_price[0, 0])
    X = np.roll(X, -1)
    X[0, 59] = predicted_stock_price[0, 0]
    #print(X)
    
  

def plotit(real_stock_price, predicted_stock_price):
  #real_stock_price = X
  plt.plot(real_stock_price, color = 'red', label = 'Real Google Stock Price')
  a = np.average(real_stock_price)
  p = np.zeros((60, 1))
  p.fill(a)
  print(p)
  predicted_stock_price = np.concatenate((p, predicted_stock_price), axis = 0)
  plt.plot(predicted_stock_price, color = 'blue', label = 'Predicted Google Stock Price')
  plt.title('Google Stock Price Prediction')
  plt.xlabel('Time')
  plt.ylabel('Google Stock Price')
  plt.legend()
  #plt.show() # SAVE IT
  print(settings.PROJECT_ROOT)
  final_path = settings.PROJECT_ROOT + '/user/static/img/image.png'
  plt.savefig(final_path)






def getStocks(request):
        # mydict = {'Microsoft':'MSFT','Google':'GOOG','Barclays':'BCS','JP Morgan Chase':'JPM','Bank of america':'bac'}
        # 		#'Infosys':'infy','Tata Motors':'ttm','Berkshire':'berk','toyota':'tm','apple':'aapl',
        # 		#'amazon':'amzn','Tesla':'tsla','Berkshire Hathaway':'brk.a','Facebook':'fb','Twitter':'twtr'}
        # for i  in mydict.values():
        # 	s = Stocks()
        # 	param = {
        # 	'q': "AAPL", # Stock symbol (ex: "AAPL")
  #       'i': "86400", # Interval size in seconds ("86400" = 1 day intervals)
  #       'x': "NASD", # Stock exchange symbol on which stock is traded (ex: "NASD")
  #       'p': "1M"
        # 	}
        # 	df = get_price_data(param)
        # 	s.description = list(mydict.keys())[list(mydict.values()).index(i)]
        # 	print(df)
  print('here')
  filename = os.path.dirname(os.path.realpath(__file__)) + '/btc.npy'

  X = X_train = np.load(filename)

  training_set_scaled, sc = scaling(X_train)
  model = os.path.dirname(os.path.realpath(__file__)) + '/hundred_epochs.pkl'
  regressor = load_model(model)
  predicted_stock_price = test_sol(X_train, sc, regressor)
  real_stock_price = X_train

  # perpetual()

  A = real_stock_price.reshape(-1, 1)
  temp = A[-60:].reshape(1, 60)
  # print(temp)
  say = A[0:60, 0].reshape(60, 1)
  perpetual(5, temp, sc, regressor)
  F = np.array(future)
  F = F.reshape(F.shape[0], 1)
  B = predicted_stock_price.reshape(-1, 1)
  B = np.concatenate((B, F), axis=0)
  ##B = np.concatenate((B, F), axis=0)
  # for i, j in zip(A, B):
  #  print(i, j)
  # from datetime import datetime
  # from datetime import timedelta
  # date = datetime.strptime(dates[-1], '%Y-%m-%d')
  # print(date)
  plotit(A, B)
  # print()
  # return render(request, 'stockpage.html')

  return render(request, 'stockpage.html')


def login(request):
  return render(request, 'login.html')


def enter(request):
  if User.objects.filter(username=request.POST.get('username'), password=request.POST.get('password')).exists():
    u = User.objects.get(username=request.POST['username'])
    request.session['usid'] = u.id
    context = {'user': u}
    return render(request, 'home.html', context)
  else:
    e = "User doesn't exist"
  return render(request, 'landingpage.html', {'error': e})


def home(request):
  usr = User.objects.filter(id=request.session['usid'])
  for i in usr:
    u = i
  return render(request, 'landingpage.html', {'u': u})


def stock(request):
  stock_list = Stocks.objects.all()
  return render(request, 'stockpage.html', {'Stocks': stock_list})


def signup(request):
  return render(request, 'signup.html')


def register(request):
  u = User()
  u.email = request.POST.get('email')
  u.name = request.POST.get('name')
  u.password = request.POST.get('password')
  u.mobile = request.POST.get('mobile')
  u.username = request.POST.get('username')
  error = ""
  if(u.password == request.POST.get('reppassword')):
    u.save()
    return render(request, 'login.html')
  else:
    error = "Password didn't match"

  return render(request, 'signup.html', {"error": error})


def mystock(request):
  s = Stocks.objects.all()
  t = Transaction.objects.filter(user=request.session['usid'])
  us = []
  st = []

  for j in t:
    us.append(j.stock)

  # print("jdygf",us)
  for i in s:
    if i.name in us:
      st.append(i)
  print("user", st)
  return render(request, 'profile.html', {'st': us})


def profile(request):
  usr = User.objects.filter(id=request.session['usid'])
  for i in usr:
    u = i
  return render(request, 'home.html', {'u': u})


def deleteStocks(request, slug):
  s = Stocks.objects.filter(id=slug)
  usr = User.objects.filter(id=request.session['usid'])
  for j in s:
    for i in usr:
      u = Transaction.objects.filter(user=i, stock=j)
      for j in u:
        loss = j.Val
        j.delete()

  usr = User.objects.filter(id=request.session['usid'])
  for i in usr:
    no = i.stock_no
    val = i.portfolio_val

  #Transaction.objects.filter(user=request.session['usid'],stock = slug).delete()
  usr.update(stock_no=no - 1, portfolio_val=val - loss)
  return render(request, 'stockpage.html')


def addStocks(request, slug):
  s = Stocks.objects.filter(id=slug)
  s.update(quantity=int(request.POST.get('qts')))
  u = User.objects.filter(id=request.session['usid'])

  for i in u:
    uuu = i

  for i in s:
    sss = i
    cls = i.close
    #new.stock = slug

  # new.save()
  if request.method == 'POST':

    v = cls * int(request.POST.get('qts'))
    u = User.objects.filter(id=request.session['usid'])
    for i in u:
      p = i.stock_no
      port = i.portfolio_val
      #p = i.stock
    #slug = p.append(slug)
    t = Transaction(stock=sss, user=uuu, quantity=int(
        request.POST.get('qts')), Val=v)
    t.save()
    u = User.objects.filter(id=request.session['usid']).update(
        stock_no=p+1, portfolio_val=port+v)

  return render(request, 'stockpage.html')


def logout(request):
  return render(request, 'login.html')


def about(request):
  return render(request, 'about.html')


def know(request):
  return render(request, 'Jargons.html')
