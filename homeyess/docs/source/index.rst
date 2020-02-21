.. homeyess documentation master file, created by
   sphinx-quickstart on Tue Feb 18 21:47:18 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to homeyess's documentation!
====================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Models
======
.. automodule:: website.models
.. autoclass:: website.models.Profile
   :members:
.. autoclass:: website.models.Ride
   :members:
.. autoclass:: website.models.JobPost
.. autoclass:: website.models.RideRequestPost

Views
=====
.. automodule:: website.views
.. automethod:: website.views.index
.. automethod:: website.views.RequestRideCreate
.. automethod:: website.views.ViewRideForm
.. automethod:: website.views.RequestRideEdit

