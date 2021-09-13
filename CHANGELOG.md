# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
## [0.3.8] - 2021-09-13
### Changed
- Support for multiple instance

## [0.3.7] - 2021-08-08
### Changed
- Remove filesRequired restriction from multiple forms
- Redirect to the payed month after create a new_salary
- Able to delete unpayed orders
### Fixed
- from_pos field not being update
## [0.3.6] - 2021-08-07
### Fixed
- NoneType loop when files being empty in new_salary's form
## [0.3.5] - 2021-08-07
### Fixed
- Default date in some form showing the date of the service launch
## [0.3.4] - 2021-08-02
### Changed
- Now in RevenueForm ask for actual value instead fee, fee will be calculated
### Fixed
- Missing translation of from_pos in LaborExpense

## [0.3.3] - 2021-07-31
### Fixed
- Order's value now can be updated to negative value
## [0.3.2] - 2021-07-31
### Changed
- Order selection in OrderPayment won't close after each selection
- Order's value now can be negative
### Fixed
- Missing remark field of `order`
## [0.3.1] - 2021-07-31
### Added
- Unpay value in Supplier's detail page and Order's index page
### Changed
- Move the position of links to detail page in the Supplier's index page
- File field in new_salary is removed
### Fixed
- Missing select2 for supplier field in `order.new`
- Some missing translation

## [0.3.0] - 2021-07-31
### Added
- New `income` module
  + `Income` and `Revenue` model
  + Relative `File` model
  + Relatives forms, views and tests
- Add `is_bank` flag in `Supplier` model
- Add `from_pos` flag in `Expense` model
- New `expense` module
  + `Expense`, `LaborExpense`, `NonLaborExpense` and `SalaryPayment` model
  + Relative `File` model
  + Relatives forms, views and tests
- Add `expense` content to `employee`, `supplier` and `order` pages
- New `order` module, including relatives database model, forms, views and tests

### Changed
- Improve CSS/HTML
- Improve handler for session timeout
- Finer permission for each endpoint
- Improve tables' pagination
- Improve `order.index` endpoint with pagination
### Fixed
- Typo of `Cancel` button and change it's CSS for consistency

## [0.2.1] - 2021-06-30
### Fixed
- Fix missing log when visit `employee.export` and `supplier.export`

## [0.2.0] - 2021-06-30
### Added
- Add schedule job to remove files that has been 'deleted' by user more than 30 days ([#77](https://github.com/HenriqueLin/CityWok-Manager/pull/77))
- Add functionality to export employee and supplier data to csv and excel file ([#74](https://github.com/HenriqueLin/CityWok-Manager/pull/74))
- Add accountant_id field to employee model to keep track the employee's id in accountant's system ([#63](https://github.com/HenriqueLin/CityWok-Manager/pull/63))
### Changed
- Open download page in new tab of browser ([#76](https://github.com/HenriqueLin/CityWok-Manager/pull/76))
- Now the session will expire after 1 hour without activities ([#71](https://github.com/HenriqueLin/CityWok-Manager/pull/71))
- Make the table in index page of employee and supplier module sortable ([#70](https://github.com/HenriqueLin/CityWok-Manager/pull/70))
- Now uploaded `.pdf`, `.png` and `.jpeg` files will be compressed to reduce the disk usage ([#62](https://github.com/HenriqueLin/CityWok-Manager/pull/62))

### Fixed
- Fix missing ZH translation of `SEX` and `ID` in `utils/__init__.py` ([#61](https://github.com/HenriqueLin/CityWok-Manager/pull/61))


## [0.1.0] - 2021-06-25
### Added
- First version ready to deploy