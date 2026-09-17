# -*- coding: utf-8 -*-
# Part of Keypress IT Services. See LICENSE file for full copyright and licensing details.##
##################################################################################


from odoo import fields, models


class Website(models.Model):
    """Adds the fields for breadcum."""

    _inherit = 'website'
    
    is_share = fields.Boolean(string="Is Share")
    dynamic_share = fields.Boolean(string="Dynamic Share")
    # type = fields.Selection([('style_1', 'Style - 1'), ('style_2', 'Style - 2')])
    fb_visible = fields.Boolean(string="Facebook",help="Enable facebook icon on product pages.")
    linkedin_visible = fields.Boolean(string="Linkedin",help="Enable Linkedin icon on product pages.")
    twitter_visible = fields.Boolean(string="Twitter",help="Enable Twitter icon on product pages.")
    email_visible = fields.Boolean(string="Email",help="Enable Email icon on product pages.")
    gmail_visible = fields.Boolean(string="Gmail",help="Enable Gmail icon on product pages.")
    whatsApp_visible = fields.Boolean(string="WhatsApp",help="Enable WhatsApp icon on product pages.")
    telegram_visible = fields.Boolean(string="Telegram",help="Enable Telegram icon on product pages.")
    pocket_visible = fields.Boolean(string="Pocket",help="Enable Pocket icon on product pages.")
    pinterest_visible = fields.Boolean(string="Pinterest",help="Enable Pinterest icon on product pages.")
    reddit_visible = fields.Boolean(string="Reddit",help="Enable Reddit icon on product pages.")
    flipboard_visible = fields.Boolean(string="Flipboard",help="Enable Flipboard icon on product pages.")
    fbm_visible = fields.Boolean(string="Facebook Messenger",help="Enable Facebook Messenger icon on product pages.")
    line_visible = fields.Boolean(string="Line",help="Enable Line icon on product pages.")
    viber_visible = fields.Boolean(string="Viber",help="Enable Viber icon on product pages.")
    wechat_visible = fields.Boolean(string="WeChat",help="Enable WeChat icon on product pages.")
    sms_visible = fields.Boolean(string="SMS",help="Enable SMS icon on product pages.")
    skype_visible = fields.Boolean(string="Skype",help="Enable Skype icon on product pages.")
    copylink_visible = fields.Boolean(string="Copy Link",help="Enable Copy Link icon on product pages.")
    evernote_visible = fields.Boolean(string="Evernote",help="Enable Evernote icon on product pages.")