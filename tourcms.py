import datetime as dt
import calendar
import urllib
import xmltodict
import hmac
import hashlib
import base64

__author__ = 'Inbal Elmaleh'
__version__ = '0.0.1'
__license__ = 'BSD'

# self:
# marketp_id(int)
# private_key
# result_type
# base_url

# TODO: for all new funcs, check param names and structures to make sure they match
# TODO: re-add logger
# TODO: test you lazy bastard, test

class Connection(object):
  def __init__(self, marketp_id, private_key, result_type = "raw"):
    try:
      int(marketp_id)
    except ValueError:
      raise TypeError("Marketplace ID must be an Integer")

    self.marketp_id = int(marketp_id)
    self.private_key = private_key
    self.result_type = result_type
    self.base_url = "https://api.tourcms.com"

  def _generate_signature(self, path, verb, channel, outbound_time):
        
    string_to_sign = f"{channel}/{self.marketp_id}/{verb}/{outbound_time}{path}"
    print(string_to_sign)

    dig = hmac.new(self.private_key.encode('utf8'),
                   string_to_sign.encode('utf8'),
                   hashlib.sha256)
    b64 = base64.b64encode(dig.digest())

    return urllib.parse.quote_plus(b64)

  def _response_to_native(self, response):
    try:
      return xmltodict.parse(response)['response']
    except KeyError:
      return xmltodict.parse(response)
    except NameError:
      return response

  def _request(self, path, channel = 0, params = {}, verb = "GET"):
    
    path_with_params = path + "?" + urllib.parse.urlencode(params)
    url = self.base_url + path_with_params
    req_time = dt.datetime.utcnow()
    
    signature = self._generate_signature(
      path_with_params , verb, channel,int(calendar.timegm(req_time.timetuple()))
    )
    
    headers = {
      "Content-type": "text/xml",
      "charset": "utf-8", 
      "x-tourcms-date": req_time.strftime("%a, %d %b %Y %H:%M:%S GMT"), 
      "Authorization": f"TourCMS {channel}:{self.marketp_id}:{signature}"
    }

    print(f"Content-type: {headers['Content-type']}")
    print(f"x-tourcms-date: {headers['x-tourcms-date']}")
    print(f"Authorization: {headers['Authorization']}")

    req = urllib.request.Request(url)
    
    for key, value in headers.items():
      req.add_header(key, value)
    
    response = urllib.request.urlopen(req).read()

    return response if self.result_type == "raw" else self._response_to_native(response)


  # HOUSEKEEPING
  def api_rate_limit_status(self, channel = 0):
    return self._request("/api/rate_limit_status.xml", channel)

  # CHANNELS  
  def list_channels(self):
    return self._request("/p/channels/list.xml")
  
  def channel_performance(self, channel):
    if channel == 0:
      return(self._request('/p/channels/performance.xml'), channel)
    else:
      return(self._request('/c/channel/performance.xml', channel))
	
  def show_channel(self, channel):
    return self._request("/c/channel/show.xml", channel)

  # Agents only
  def list_channel_prformance(self, channel):
    return self._request("/p/channels/performance.xml", channel)

  # TOURS
  def search_tours(self, params = {}, channel = 0):
    if channel == 0:
      return self._request("/p/tours/search.xml", 0, params)
    else:
      return self._request("/c/tours/search.xml", channel, params)

  def show_tour(self, tour, channel):
    return self._request("/c/tour/show.xml", channel, {"id": tour})

  def tour_dates_and_deals(self, params = {}, tour = "", channel = 0):
    return self._request("/c/tour/datesprices/datesndeals/search.xml", channel, {"id": tour})

  # todo: test params
  def update_tour(self, channel, tour_data):
    return self._request("/c/tour/update.xml", channel, {"update": tour_data})

  # todo: test params
  def update_tour_url(self, channel, url_data):
    return(self.update_tour(channel, {"tour": url_data}))

  def list_product_filters(self, channel = 0):
    return self._request("/c/tours/filters.xml", channel)

  def search_hotels_range(self, params = {}, tour = "", channel = 0):
    params.update({"single_tour_id": tour})
    if channel == 0:
      return self._request("/p/hotels/search_range.xml", 0, params)
    else:
      return self._request("/c/hotels/search_range.xml", channel, params)
    
  def search_hotels_specific(self, params = {}, tour = "", channel = 0):
    params.update({"single_tour_id": tour})
    if channel == 0:
      return self._request("/p/hotels/search-avail.xml", 0, params)
    else:
      return self._request("/c/hotels/search-avail.xml", channel, params)
  
  def list_tours(self, channel = 0):
    if channel == 0:
      return self._request("/p/tours/list.xml")
    else:
      return self._request("/c/tours/list.xml", channel)

  def list_tour_images(self, channel = 0):
    if channel == 0:
      return self._request("/p/tours/images/list.xml")
    else:
      return self._request("/c/tours/images/list.xml", channel)

  # todo: test params
  def list_tour_locations(self, channel, params):
    if channel == 0:
      return self._request("/p/tours/locations.xml", channel, params)
    else:
      return self._request("/c/tours/locations.xml", channel, params)

  def show_tour_departures(self, tour, channel):
    return self._request("/c/tour/datesprices/dep/show.xml", channel, {"id": tour})
  
  # todo: check params
  def search_raw_departures(self, channel, tour, params):
    params.update({"id": tour})
    return self._request("/c/tour/datesprices/dep/manage/search.xml", channel, params)

  # todo: check params
  def show_departure(self, channel, tour, departure):
    return self._request("/c/tour/datesprices/dep/manage/show.xml", channel,
                        {"id": tour, "departure": departure})

  # todo: check params
  def create_new_departure(self, channel, departure_data):
    return self._request("/c/tour/datesprices/dep/manage/new.xml", channel,
                        {"departure_data": departure_data}, verb="POST")
  
  # todo: check params
  def update_departure(self, channel, departure_data):
    return self._request("/c/tour/datesprices/dep/manage/update.xml", channel,
                        {"departure_data": departure_data}, verb="POST")
  
  # todo: check params
  def delete_departure(self, channel, tour, departure):
    return self._request("/c/tour/datesprices/dep/manage/update.xml", channel,
                        {"tour_id": tour, "departure": departure}, verb="POST")

  # todo: does this still exist?
  def show_tour_freesale(self, tour, channel):
    return self._request("/c/tour/datesprices/freesale/show.xml", channel, {"id": tour})

  # todo: check params
  def delete_tour(self, channel, tour):
    return self._request("/c/tours/delete.xml", channel, {"tour_id": tour}, verb="POST")

  # TODO: implement
  # upload_files
  # delete_tour_image
  # delete_tour_document

  # BOOKINGS

  # Creating bookings
  # todo: check params
  def check_tour_availability(self, channel, tour, params):
    params.update({"tour_id": tour})
    return self._request("/c/tour/datesprices/checkavail.xml", channel, params)

  # todo: check params - but should be ok
  def show_promo(self, channel, promo):
    return self._request("/c/promo/show.xml", channel, {"promo_code": promo}) 

  # todo: check params
  def get_new_booking_key(self, channel, customer_data):
    return self._request("/c/booking/new/get_redirect_url.xml", channel,
                        {"customer_data": customer_data}, verb="POST")

  # todo: check params
  def start_new_booking(self, channel, booking_data):
    return self._request("/c/booking/new/start.xml", channel,
                        {"booking_data": booking_data}, verb="POST")

  # todo: check params
  def commit_new_booking(self, channel, booking_data):
    return self._request("/c/booking/new/commit.xml", channel,
                        {"booking_data": booking_data}, verb="POST")

  # Bookings data
  # todo: check params
  def list_bookings(self, channel, params = {}):
    if channel == 0:
      return self._request("/p/bookings/list.xml", 0, params)
    else:
      return self._request("/c/bookings/list.xml", channel, params)

  # Docs have been saying it will soon be deprecated for a while.
  # PS: tourcms please don't deprecate! this one is so useful
  # todo: check params
  def search_bookings(self, channel, params = {}):
    if channel == 0:
      return self._request("/p/bookings/search.xml", 0, params)
    else:
      return self._request("/c/bookings/search.xml", channel, params)

  # todo: check params
  def show_booking(self, channel, booking):
      return self._request("/c/booking/show.xml", channel, {"booking": booking})
  
  # todo: check params
  def update_booking(self, channel, booking_data):
      return self._request("/c/booking/update.xml", channel,
                           {"booking_data": booking_data}, verb='POST')

  # todo: check params
  def add_note_to_booking(self, channel, booking, note, note_type):
      return self._request("/c/booking/note/new.xml", channel,
                           {"booking": booking, "note": note,
                            "note_type": note_type}, verb='POST')
  
  # todo: check params
  def send_booking_email(self, channel, booking_data):
      return self._request("/c/booking/email/send.xml", channel,
                           {"booking_data": booking_data}, verb='POST')
   
  # todo: check params
  def cancel_booking(self, channel, booking_data):
      return self._request("/c/booking/cancel.xml", channel,
                           {"booking_data": booking_data}, verb='POST')

  # todo: check params
  def delete_booking(self, channel, booking_data):
      return self._request("/c/booking/delete.xml", channel,
                           {"booking_data": booking_data}, verb='POST')

  # todo: check params
  def check_option_availability(self, channel, booking, component_data):
    return self._request("/c/booking/options/checkavail.xml", channel,
                         {"booking": booking, "component_data": component_data})
 
  # todo: check params
  def update_booking_component(self, channel, component_data):
      return self._request("/c/booking/component/update.xml", channel,
                           {"component_data": component_data}, verb='POST')
  
  # todo: check params
  def add_booking_component(self, channel, component_data):
      return self._request("/c/booking/component/new.xml", channel,
                           {"component_data": component_data}, verb='POST')

  # todo: check params
  def remove_booking_component(self, channel, component_data):
      return self._request("/c/booking/component/delete.xml", channel,
                           {"component_data": component_data}, verb='POST')

  # PAYMENTS

  # todo:
  # create_payment
  # log_failed_payment
  # spreedly_create_payment
  # spreedly_complete_payment


  # todo: check params
  def record_payment_or_refund(self, channel, payment):
    return self._request("/c/booking/new/commit.xml", channel,
                        {"payment": payment}, verb="POST")
  
  # todo: check params
  def create_spreedly_payment(self, channel, payment):
    return self._request("/c/booking/payment/spreedly/new.xml", channel,
                        {"payment": payment}, verb="POST")
  
  # todo: check params
  def list_payments(self, channel, qs):
    return self._request("/c/booking/payment/list.xml", channel, {"qs": qs})
  
  # VOUCHERS
  # todo: check params
  def search_voucher(self, channel, voucher_data):
    return self._request("/c/voucher/search.xml", channel,
                        {"voucher_data": voucher_data}, verb="POST")
  
  # todo: check params
  def redeem_voucher(self, channel, voucher_data):
    return self._request("/c/voucher/redeem.xml", channel,
                        {"voucher_data": voucher_data}, verb="POST")
  
  # CUSTOMERS & ENQUIRIES
  # todo: check params
  def create_customer_or_enquiry(self, channel, enquiry_data):
    return self._request("/c/enquiry/new.xml", channel,
                        {"enquiry_data": enquiry_data}, verb="POST")
  
  # todo: check params
  def search_enquiries(self, channel, params):
    if channel == 0:
      return self._request("/p/enquiries/search.xml", channel, params)
    else:
      return self._request("/c/enquiries/search.xml", channel, params)
  
  # todo: check params
  def show_enquiry(self, channel, enquiry):
    return self._request("/c/enquiry/show.xml", channel, {"enquiry": enquiry})

  # todo: check params
  def show_customer(self, channel, customer):
    return self._request("/c/customer/show.xml", channel, {"customer": customer})
  
  # todo: check params
  def update_customer(self, channel, customer_data):
      return self._request("/c/customer/update.xml", channel,
                           {"customer_data": customer_data}, verb='POST')
  
  # todo: check params
  def search_customer_login(self, channel, username, password):
    return self._request("/c/customers/login_search.xml", channel,
                         {"username": username, "password": password})
  
  # AGENTS (Tour Operator use only)
  # todo: check params
  def search_travel_agent(self, channel, params):
    return self._request("/c/agents/search.xml", channel, params)
  
  # todo: check params
  def update_agent(self, channel, agent_data):
    return self._request("/c/agents/update.xml", channel,
                         {"update": agent_data}, verb="POST")
  
  # todo: Travel Agent login via API - are there more funcs?
  def start_new_agent_login(self, channel, params):
    return self._request("/c/start_agent_login.xml", channel, params, verb="POST")
  
  def retrieve_agent_booking_key(self, channel, private_token):
    return self._request("/c//c/retrieve_agent_booking_key.xml", channel, {"k": private_token})

  # INTERNAL SUPPLIERS (Tour Operator use only)
  def show_supplier(self, supplier, channel):
    return self._request("/c/supplier/show.xml", channel, {"supplier_id": supplier})

  # STAFF MEMBERS (Tour Operator use only)
  def list_staff_members(self, channel):
    return self._request("/c/staff/list.xml", channel)
  
  # PICKUP POINTS (Tour Operator use only)
  # todo: check params
  def create_new_pickup(self, channel, pickup_data):
    return self._request("/c/pickups/new.xml", channel,
                         {"pickup_data": pickup_data}, verb="POST")
  
  # todo: check params
  def delete_pickup(self, channel, pickup_data):
    return self._request("/c/pickups/delete.xml", channel,
                         {"pickup_data": pickup_data}, verb="POST")
  
  # todo: check params
  def update_pickup(self, channel, pickup_data):
    return self._request("/c/pickups/update.xml", channel,
                         {"pickup_data": pickup_data}, verb="POST")
  
  # todo: list_pickups