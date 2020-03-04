
def filterQuerySet(jobs, location, job_title):
    '''Filters the list of jobs based on location and job title specified

    :param jobs: The list of all jobs we are filtering
    :type request: list
    :param location: A location used to filter certain jobs
    :type request: string
    :param job_title: Job title provided by user to filter certain jobs
    :type request: string
    :return: The list of all jobs that were found based on the filter
    :rtype: list
    '''

    # If no filter has been applied, don't filter:
    if location is None and job_title is None:
        return jobs

    # This way we can filter if only one of the values is set:
    loc_filter = location.lower() if location is not None else ''
    title_filter = job_title.lower() if job_title is not None else ''

    return list(filter(lambda job: (loc_filter in job.location.lower()) and (title_filter in job.job_title.lower()), jobs))
