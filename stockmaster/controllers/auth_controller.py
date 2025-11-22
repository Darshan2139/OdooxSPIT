# -*- coding: utf-8 -*-

import random
import string
from odoo import http, fields
from odoo.http import request
from odoo.exceptions import ValidationError, UserError


class AuthController(http.Controller):

    @http.route('/stockmaster/signup', type='json', auth='public', methods=['POST'], csrf=False)
    def signup(self, name, email, password, **kwargs):
        """User signup endpoint"""
        try:
            if not name or not email or not password:
                return {'error': 'Name, email, and password are required'}
            
            # Check if user already exists
            existing_user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if existing_user:
                return {'error': 'User with this email already exists'}
            
            # Create new user
            user_vals = {
                'name': name,
                'login': email,
                'email': email,
                'password': password,
                'groups_id': [(6, 0, [request.env.ref('stockmaster.group_warehouse_staff').id])],
            }
            
            user = request.env['res.users'].sudo().create(user_vals)
            
            # Login the user
            request.session.authenticate(request.session.db, email, password)
            
            return {
                'success': True,
                'message': 'Account created successfully',
                'redirect': '/web#action=stockmaster.action_dashboard'
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/stockmaster/login', type='json', auth='public', methods=['POST'], csrf=False)
    def login(self, email, password, **kwargs):
        """User login endpoint"""
        try:
            if not email or not password:
                return {'error': 'Email and password are required'}
            
            # Authenticate user
            uid = request.session.authenticate(request.session.db, email, password)
            
            if uid:
                return {
                    'success': True,
                    'message': 'Login successful',
                    'redirect': '/web#action=stockmaster.action_dashboard'
                }
            else:
                return {'error': 'Invalid email or password'}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/stockmaster/forgot-password', type='json', auth='public', methods=['POST'], csrf=False)
    def forgot_password(self, email, **kwargs):
        """Generate OTP for password reset"""
        try:
            if not email:
                return {'error': 'Email is required'}
            
            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if not user:
                return {'error': 'User with this email does not exist'}
            
            # Generate 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Store OTP in user's record (in a real system, use a separate model with expiration)
            user.sudo().write({'otp_code': otp, 'otp_expiry': fields.Datetime.now()})
            
            # In production, send OTP via email/SMS
            # For MVP, we'll return it (remove in production!)
            return {
                'success': True,
                'message': 'OTP sent to your email',
                'otp': otp  # Remove this in production!
            }
        except Exception as e:
            return {'error': str(e)}

    @http.route('/stockmaster/reset-password', type='json', auth='public', methods=['POST'], csrf=False)
    def reset_password(self, email, otp, new_password, **kwargs):
        """Reset password using OTP"""
        try:
            if not email or not otp or not new_password:
                return {'error': 'Email, OTP, and new password are required'}
            
            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if not user:
                return {'error': 'User with this email does not exist'}
            
            # Verify OTP (in production, check expiry too)
            if not hasattr(user, 'otp_code') or user.otp_code != otp:
                return {'error': 'Invalid or expired OTP'}
            
            # Reset password
            user.sudo().write({'password': new_password, 'otp_code': False})
            
            return {
                'success': True,
                'message': 'Password reset successfully',
                'redirect': '/web/login'
            }
        except Exception as e:
            return {'error': str(e)}

