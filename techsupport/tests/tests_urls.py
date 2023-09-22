from techsupport import tests
from django.test import SimpleTestCase
from django.urls import reverse, resolve
from uuid import uuid4
from techsupport.views import (
    user_login,
    user_logout,
    dashboard,
    profile,
    ticket_details,
    create_ticket,
    all_tickets,
    # settings_view,
    assign_ticket,
    open_tickets,
    resolved_tickets,
    tickets_in_progress,
    get_subcategories,
    export_tickets_csv,
)

class TestUrls(SimpleTestCase):
    
    def test_login_url_is_resolves(self):
        url = reverse('login')
        self.assertAlmostEquals(resolve(url).func, user_login)
        
    def test_logout_url_is_resolves(self):
        url = reverse('logout')
        self.assertAlmostEquals(resolve(url).func, user_logout)
    
    def test_dashboard_url_is_resolves(self):
        url = reverse('dashboard')
        self.assertAlmostEquals(resolve(url).func, dashboard)    
    
    def test_profile_url_is_resolves(self):
        url = reverse('profile')
        self.assertAlmostEquals(resolve(url).func, profile)
        
    def test_ticket_details_url_is_resolves(self):
        ticket_id = uuid4()
        url = reverse('ticket_details', kwargs={'ticket_id': ticket_id})
        self.assertAlmostEquals(resolve(url).func, ticket_details)
    
    def test_create_ticket_url_is_resolves(self):
        url = reverse('create_ticket')
        self.assertAlmostEquals(resolve(url).func, create_ticket)
        
    def test_all_tickets_url_is_resolves(self):
        url = reverse('all_tickets')
        self.assertAlmostEquals(resolve(url).func, all_tickets)
        
    def test_assign_ticket_url_is_resolves(self):
        url = reverse('assign_ticket')
        self.assertAlmostEquals(resolve(url).func, assign_ticket)
        
    def test_open_tickets_url_is_resolves(self):
        url = reverse('open_tickets')
        self.assertAlmostEquals(resolve(url).func, open_tickets)
        
    def test_resolved_tickets_url_is_resolves(self):
        url = reverse('resolved_tickets')
        self.assertAlmostEquals(resolve(url).func, resolved_tickets)
        
    def test_tickets_in_progress_url_is_resolves(self):
        url = reverse('tickets_in_progress')
        self.assertAlmostEquals(resolve(url).func, tickets_in_progress)
        
        
    def test_get_subcategories_url_is_resolves(self):
        url = reverse('get_subcategories')
        self.assertAlmostEquals(resolve(url).func, get_subcategories)      
    
    def test_export_tickets_csv_url_is_resolves(self):
        url = reverse('export_tickets_csv')
        self.assertAlmostEquals(resolve(url).func, export_tickets_csv)