from flask import Blueprint, current_app, flash, redirect, render_template, url_for
income_bp = Blueprint("income", __name__, url_prefix="/income")


