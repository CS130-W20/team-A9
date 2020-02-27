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
.. automethod:: website.views.signup
.. automethod:: website.views.dashboard
.. automethod:: website.views.homeless
.. automethod:: website.views.company
.. automethod:: website.views.volunteer
.. autoclass:: website.views.RequestRideCreate
  :members:
.. automethod:: website.views.viewrideform
.. autoclass:: website.views.RequestRideEdit
  :members:
.. automethod:: website.views.editjob
.. automethod:: website.views.postjob

Forms
=====
.. automodule:: website.forms
.. autoclass:: website.forms.SignUpForm
  :members:
.. autoclass:: website.forms.PostJobForm
  :members:
.. autoclass:: website.forms.RideRequestForm
  :members:

