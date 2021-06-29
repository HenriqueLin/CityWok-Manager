# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [Unreleased]

### Added
- Add accountant_id field to employee model to keep track the employee's id in accountant's system ([#63](https://github.com/HenriqueLin/CityWok-Manager/pull/63]))
### Changed
- Now the session will expire after 1 hour without activities ([#71](https://github.com/HenriqueLin/CityWok-Manager/pull/71))
- Make the table in index page of employee and supplier module sortable ([#70](https://github.com/HenriqueLin/CityWok-Manager/pull/70))
- Now uploaded `.pdf`, `.png` and `.jpeg` files will be compressed to reduce the disk usage ([#62](https://github.com/HenriqueLin/CityWok-Manager/pull/62))

### Fixed
- Fix missing ZH translation of `SEX` and `ID` in `utils/__init__.py` ([#61](https://github.com/HenriqueLin/CityWok-Manager/pull/61))


## [0.1.0] - 2021-06-25
### Added
- First version ready to deploy