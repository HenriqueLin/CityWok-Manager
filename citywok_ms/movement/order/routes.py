from flask import Blueprint, flash, redirect, url_for, render_template, current_app

order_bp = Blueprint("order", __name__, url_prefix="/order")


