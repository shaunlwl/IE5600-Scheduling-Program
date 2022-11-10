import datetime as dt
import csv


def createCalendarRange(start_date, end_date, calendar_resource_dict, list_of_employees):
    '''This function initialises the date range (using a dictionary) for which our scheduling application works, data structure is three dimensional in nature'''
    if calendar_resource_dict == {}: #Safeguard to ensure that Calendar is not initialised twice
        sd = dt.datetime.strptime(start_date, '%Y-%m-%d')
        ed = dt.datetime.strptime(end_date, '%Y-%m-%d')
        delta = ed - sd
        # Structure of the dictionary is as such --> {date: [List of employees in dictionary{employee number: available hour, Craft: Craft},...,{}]}
        for i in range(delta.days+1):
            for employee in list_of_employees:
                if sd + dt.timedelta(days=i) not in calendar_resource_dict:
                    calendar_resource_dict[sd + dt.timedelta(days=i)] = [{employee.getEmpId(): employee.getTotalHoursPerDay(), "Craft" : employee.getCraft()}]
                else:
                    calendar_resource_dict[sd + dt.timedelta(days=i)].append({employee.getEmpId():employee.getTotalHoursPerDay(), "Craft" : employee.getCraft()})
        
        #Calendar data structure is created for date range given as per calendar_start_date and calendar_end_date
        print("\n** Resource Tool initialised, Tool has been set up for use **""\n""")
        
    else:
        print("ERROR: You have already initialised the Resource Calendar""\n""")






def scheduleJob(job_name, start_date, due_date, resources, total_cost, craft ,calendar_resource_dict, current_job_id, list_of_jobs):
    '''This function only runs when there are sufficient resources within the time period of start date and due date and user confirms schedule (i.e scheduleJobCheck returns True)'''
    #Job Object is created and appended to list_of_jobs
    job_id = "#" + str(current_job_id)
    list_of_jobs.append(job(job_id, job_name, start_date, due_date, resources, total_cost, craft))
    job_start_date = start_date

    #Resource in the calendar data structure is reduced accordingly as per the Job requirements
    while start_date <= due_date  and resources !=0:
        for employee in calendar_resource_dict[start_date]:
            if list(employee.values())[0] == 0:
                continue
            if list(employee.values())[0] != 0 and resources >= list(employee.values())[0] and list(employee.values())[1].lower() == craft.lower(): #[0] is the index for the employee attribute of TotalHoursPerDay and [1] is the index for employee attribute Craft
                resources = resources - list(employee.values())[0]
                if start_date not in list(list_of_jobs[-1].employees.keys()): #if the start date is not a key in the job.employee attribute, save the start date as key
                    list_of_jobs[-1].employees[start_date] = [{list(employee.keys())[0]: list(employee.values())[0]}] #the job.employees attribute will look like this: {2022-01-02: [{emp_id: TotalHoursPerDay}]}
                    # list_of_jobs[-1] will be the job of interest, which is the latest addition
                else:
                    list_of_jobs[-1].employees[start_date].append({list(employee.keys())[0]: list(employee.values())[0]}) #deduct the available time to be 0 in the calendar dictionary
                
                employee[list(employee.keys())[0]]= 0

                if resources == 0:
                    list_of_jobs[-1].scheduled_end_date = start_date
                    break
                
                # resource required is less than the free hours.
            elif list(employee.values())[0] != 0 and resources < list(employee.values())[0] and list(employee.values())[1].lower() == craft.lower():
                employee[list(employee.keys())[0]]= list(employee.values())[0] - resources  # minus required resource from the available free hour for the employee
                if start_date not in list(list_of_jobs[-1].employees.keys()):
                    list_of_jobs[-1].employees[start_date] = [{list(employee.keys())[0]: resources}]
                else:
                    list_of_jobs[-1].employees[start_date].append({list(employee.keys())[0]: resources})
                
                resources = resources- resources #resources = 0
                
                if resources == 0:
                    list_of_jobs[-1].scheduled_end_date = start_date
                    break
            
            else:
                continue # go to the next employee
        start_date += dt.timedelta(days=1)
    
    #Print out to User
    print("\nSUCCESS! Job '{}' has been scheduled with ID {} and Start date: {}\n".format(job_name, job_id, job_start_date.date()))
    print("Here are the allocated employee IDs and their allocated work hours for this job: \n(i.e. Date: yyyy-mm-dd --> [{Employee ID: Work Hour(s)}])")
    print("--" * 40)
    for dates in list_of_jobs[-1].employees:
        print("      Date: {} --> {}".format(dates.date(),list(list_of_jobs[-1].employees[dates])))
        print("--" * 40)
    



def scheduleJobCheck(job_name, start_date, due_date, resources, total_cost, craft, calendar_resource_dict, calendar_start_date, calendar_end_date):
    total_available_hours_within_period = 0
    
    current_date = start_date

    #Checks if given dates by the user when scheduling a job has available resources    
    while current_date < due_date + dt.timedelta(days=1):
        for employee in calendar_resource_dict[current_date]: # get all employees
            if list(employee.values())[1].lower() == craft.lower(): # check if same craft
                total_available_hours_within_period += list(employee.values())[0] # add up all available resources
            else:
                continue
        current_date += dt.timedelta(days=1)


    #If sufficient resource, return True and the given dates by User, Else, return False, so that scheduleJob() function will not be called
    if total_available_hours_within_period >= resources:
        while True:
            user_input = input("Job can be scheduled, do you want to proceed? Y/N""\n""").lower()
            if user_input in ["y", "n"]:
                break
            else:
                print("ERROR: You have entered an invalid selection, Please try again""\n""")
        if user_input == "y":
            return True, start_date, due_date
                
        else:
            return False, None, None
    #If insufficient resources, prompt user if they would like a recommended schedule, if yes, recommendSchedule() function is called      
    else:
        while True:
            user_input = input("Job cannot be scheduled due to unavailable resources, do you want to check for earliest available slot? Y/N""\n""").lower()
            if user_input in ["y", "n"]:
                break
            else:
                print("ERROR: You have entered an invalid selection, Please try again""\n""")
        if user_input == "y":
            new_start_date, new_end_date = recommendSchedule(resources, start_date, due_date, craft, calendar_resource_dict, calendar_start_date, calendar_end_date)
            #Provide the recommended dates to the User for the case of single day completion
            if new_end_date == None and new_start_date != None:
                while True:
                    user_input = input("Job can be scheduled and fully completed on this date: {}, do you want to schedule it? Y/N""\n""".format(new_start_date.date())).lower()
                    if user_input in ["y", "n"]:
                        break
                    else:
                        print("ERROR: You have entered an invalid selection, Please try again""\n""")
                if user_input == "y":
                    return True, new_start_date, new_start_date
                else:
                    return False, None, None                       
            #Provide the recommended dates to the User for the case of multiple days required for Job completion         
            elif new_start_date != None and new_end_date != None:
                while True:
                    user_input = input("Job can be scheduled from Start date: {} --> End date: {}, do you want to schedule it? Y/N""\n""".format(new_start_date.date(), new_end_date.date())).lower()
                    if user_input in ["y", "n"]:
                        break
                    else:
                        print("ERROR: You have entered an invalid selection, Please try again""\n""")
                if user_input == "y":
                    return True, new_start_date, new_end_date
                else:
                    return False, None, None  
            else:
                return False, None, None
        else:
            return False, None, None        



        


def recommendSchedule(resources, start_date, due_date, craft, calendar_resource_dict, calendar_start_date, calendar_end_date):
    '''This function returns the best available schedule for the current job based on either the flexibility of the start date or due date'''
    while True:
        user_input = input("Please input which of the job dates is flexible - \n1 : Start Date, or \n2 : Due Date \nInput (1) or (2): ")
        
        #Case when Job Due Date is flexible (Job start date will be fixed)
        if user_input == "2":
            current_date = start_date
            recommended_date_range = []
            while resources != 0:
                for employee in calendar_resource_dict[current_date]:
                    if list(employee.values())[1].lower() == craft.lower() and list(employee.values())[0] !=0:
                        if resources >= list(employee.values())[0]:
                            resources -= list(employee.values())[0]
                            recommended_date_range.append(current_date)
                            if resources == 0:
                                break
                        else:
                            resources -= resources
                            recommended_date_range.append(current_date)
                            break
                    else:
                        continue
                current_date += dt.timedelta(days=1)
                if current_date > calendar_end_date:
                    print("Job can only be scheduled after Resource Tool Working Range of End Date: {}, Please set the Job Start Date to be flexible and try again ""\n""".format(calendar_end_date))
                    return None, None
            if len(recommended_date_range) == 1:
                return recommended_date_range[0], None
            else:
                return recommended_date_range[0], recommended_date_range[-1]

        #Case when Job Start Date is flexible (Job Due Date will be fixed)
        elif user_input == "1":
            current_date = due_date
            recommended_date_range = []
            while resources != 0:
                for employee in calendar_resource_dict[current_date]:
                    if list(employee.values())[1].lower() == craft.lower() and list(employee.values())[0] !=0:
                        if resources >= list(employee.values())[0]:
                            resources -= list(employee.values())[0]
                            recommended_date_range.append(current_date)
                            if resources == 0:
                                break
                        else:
                            resources -= resources
                            recommended_date_range.append(current_date)
                            break
                    else:
                        continue
                current_date -= dt.timedelta(days=1)
                if current_date < calendar_start_date:
                    print("Job can only be scheduled before Resource Tool Working Range of Start Date: {}, Please set the Job Due Date to be flexible and try again""\n""".format(calendar_start_date))
                    return None, None

            if len(recommended_date_range) == 1:
                return recommended_date_range[0], None
            else:
                return recommended_date_range[-1], recommended_date_range[0]

        else:
            print("ERROR: You have entered an invalid input, Please try again""\n""")
            continue
    


#Created as a Public Class
class job:
    
    def __init__(self, job_id, job_name, start_date, due_date, resources, total_cost, craft):
        
        self.job_id = job_id #does not have to be in numerical format, can be string digits
        self.job_name = job_name
        try:
            self.start_date = start_date
            self.due_date = due_date
            self.resources = float(resources)
            self.total_cost = float(total_cost)
            self.employees = {} #To create an association to employee class (for easy reference of employees tagged to a job)
        except ValueError:
            print("ERROR: Job attribute(s) that are expected to be numerical or date format are not in the correct form, please change to numerical/date form""\n""")
            raise IOError
        self.craft = craft
        self.scheduled_end_date = None #This is the scheduled end date in the system (maybe same or different from the planned due date/deadline input by user)  
             
#Did not define getter/setter methods as Public Class

             
        
#Created as a Private Class  
class employee:
    
    def __init__(self, emp_id, first_name, last_name, hourly_rate, total_hours_per_day, competency, craft):
        
        self._first_name = first_name
        self._last_name = last_name
        try:
            self._emp_id = int(emp_id)
            self._hourly_rate = float(hourly_rate)
            self._total_hours_per_day = float(total_hours_per_day)
            self._competency = float(competency)
        except ValueError:
            print("ERROR: Employee attribute(s) that are expected to be numerical are not in the correct form, please change to numerical form""\n""")
            raise IOError
        self._craft = craft

    def getEmpId(self):
        return self._emp_id

    def setEmpId(self,emp_id):
        self._emp_id = emp_id

    def getFirstName(self):
        return self._first_name

    def setFirstName(self,first_name):
        self._first_name = first_name
    
    def getLastName(self):
        return self._last_name

    def setLastName(self,last_name):
        self._last_name = last_name

    def getHourlyRate(self):
        return self._hourly_rate

    def setHourlyRate(self,hourly_rate):
        self._hourly_rate = hourly_rate

    def getTotalHoursPerDay(self):
        return self._total_hours_per_day

    def setTotalHoursPerDay(self,total_hours_per_day):
        self._total_hours_per_day = total_hours_per_day

    def getCompetency(self):
        return self._competency

    def setCompetency(self,competency):
        self._competency = competency
    
    def getCraft(self):
        return self._craft

    def setCraft(self,craft):
        self._craft = craft


    @staticmethod
    def CurrentEmployeeList(list_of_employees, list_of_new_employees, list_of_leaving_employees, current_date):
        temp_list_of_employees = list_of_employees
        for items in list_of_leaving_employees: #list of leaving employees track the actual out of office date (last day + 1 day)
            if current_date < list(items.keys())[0]:
                continue
            else:
                i = 0
                while i < len(temp_list_of_employees):
                    if temp_list_of_employees[i].getEmpId() == list(items.values())[0]:
                        del temp_list_of_employees[i]
                        continue
                    i += 1
        
        for items in list_of_new_employees:
            if current_date >= list(items.keys())[0]:
                temp_list_of_employees.append(list(items.values())[0])  
            else:
                continue
    
        return temp_list_of_employees      

    @staticmethod      
    def addEmployee(emp_id, first_name, last_name, hourly_rate, total_hours_per_day, competency, craft, start_date, list_of_new_employees, calendar_resource_dict, calendar_end_date):
        '''This method appends a new employee to list of new employees and adds this new employee to the resource tracked in the Calendar resource data structure. This method should only be called when Calendar Resource Dict has been initialised with the createCalendarRange function'''
        employee_already_added = False
        for items in list_of_new_employees:
            if list(items.values())[0].getEmpId() == emp_id:
                employee_already_added = True
                break
        if employee_already_added == True:
            print("\nThis employee has already been recorded in the system with a scheduled start date") 
        else:
            list_of_new_employees.append( {start_date: employee(emp_id, first_name, last_name, hourly_rate, total_hours_per_day, competency, craft)})
            sd = start_date
            ed = dt.datetime.strptime(calendar_end_date,'%Y-%m-%d')
            delta = ed - sd
            for i in range(delta.days +1):
                if sd+ dt.timedelta(days=i) not in calendar_resource_dict:
                    calendar_resource_dict[sd + dt.timedelta(days=i)] = [{emp_id: total_hours_per_day, "Craft" : craft.capitalize()}]
                else:
                    calendar_resource_dict[sd + dt.timedelta(days=i)].append({emp_id: total_hours_per_day, "Craft" : craft.capitalize()})
            print("\nEmployee {} successfully added to database\n".format(emp_id))


    @staticmethod
    def removeEmployee(emp_id, last_day ,craft, list_of_leaving_employees, calendar_resource_dict, calendar_end_date, list_of_jobs):
        '''This method removes the employee from the Calendar resource data structure and automatically reschedules the affected hours of every job due to employee leaving based on last day of work + 1 day (Out of company date)'''
        employee_already_removed = False
        for items in list_of_leaving_employees:
            if list(items.values())[0] == emp_id:
                employee_already_removed = True
                break
        if employee_already_removed == True:
            print("\nThis employee has already been recorded in the system with a scheduled last working day")
        else:
            list_of_unable_to_reschedule_hours = [] #For the very edge case if reschdule date goes past calendar_end_date
            list_of_leaving_employees.append({last_day + dt.timedelta(days=1): emp_id}) #Add to list of leaving employees so that when current employee list is pulled, there will be a check with the list_of_leaving_employees first
            
            out_of_company_date = last_day + dt.timedelta(days=1) #Employee is still considered working on Last Day of Work
            
            ed = dt.datetime.strptime(calendar_end_date,'%Y-%m-%d')  
            if out_of_company_date > ed:
                print("Employee will officially leave the company past the Resource Tool working date of {}, No action required as no jobs are scheduled past {}\n".format(calendar_end_date, calendar_end_date))
            else:
                delta = ed - out_of_company_date
                for i in range(delta.days +1): 
                    for employees in calendar_resource_dict[out_of_company_date + dt.timedelta(days=i)]:
                        if list(employees.keys())[0] == emp_id:
                            calendar_resource_dict[out_of_company_date + dt.timedelta(days=i)].remove(employees) # Removes this particular employee resource from all dates in Calendar Resource starting from Last Day of Work
                
                
                affected_resources = 0
                list_of_affected_jobs_id = []
                list_of_affected_jobs = []
                for job in list_of_jobs:
                    unable_to_reschedule_hours = 0 #Only used in the very edge case that hours cannot be rescheduled due to past calendar_end_date
                    for dates in list(job.employees.keys()): #Looping through the various dates that the job is scheduled to occur
                        if dates < out_of_company_date:
                            continue
                        else:
                            length = len(job.employees[dates])
                            i=0
                            while i < length: #Looping through the employees tagged to a job on a certain date
                                if list(job.employees[dates][i].keys())[0] == emp_id:
                                    list_of_affected_jobs.append(job)
                                    list_of_affected_jobs_id.append(job.job_id)
                                    affected_resources = list(job.employees[dates][i].values())[0] #Store how many hours is affected for that day(dates)
                                    
                                    del job.employees[dates][i] # Delete the leaving employee's commitment to the job
                                    length -=1
                                    calendar_reschedule_date_loop = dates #Assign a looping variable to the dates (which signify the affected date)

                                    while affected_resources != 0: #Loop only ends when all the affected resource are rescheduled
                                        
                                        
                                        
                                        #Automatic Rescheduling Algorithm below
                                        for employees in calendar_resource_dict[calendar_reschedule_date_loop]:
                                            if list(employees.values())[0] == 0:
                                                continue

                                            elif list(employees.values())[0] != 0 and affected_resources >= list(employees.values())[0] and list(employees.values())[1].lower() == craft.lower(): #[0] is the index for the employee attribute of TotalHoursPerDay and [1] is the index for employee attribute Craft
                                                affected_resources = affected_resources - list(employees.values())[0]

                                                if calendar_reschedule_date_loop not in job.employees.keys(): 
                                                    job.employees[calendar_reschedule_date_loop] = [{list(employees.keys())[0]: list(employees.values())[0]}] #the job.employees attribute will look like this: {2022-01-02: [{emp_id: TotalHoursPerDay}]}
                                
                                                else:
                                                    employee_exist_in_key = False
                                                    index = 0
                                                    for items in job.employees[calendar_reschedule_date_loop]:
                                                        if list(items.keys())[0] == list(employees.keys())[0]:
                                                            employee_exist_in_key = True
                                                            break
                                                        index +=1

                                                    if employee_exist_in_key == True:
                                                        current_employee_resource_allocated =list(job.employees[calendar_reschedule_date_loop][index].values())[0]
                                                        job.employees[calendar_reschedule_date_loop][index] = {list(employees.keys())[0]: current_employee_resource_allocated + list(employees.values())[0]}
                                                    else:
                                                        job.employees[calendar_reschedule_date_loop].append({list(employees.keys())[0]: list(employees.values())[0]}) #deduct the available time to be 0 in the calendar dictionary
                            
                                                employees[list(employees.keys())[0]]= 0

                                                if affected_resources == 0:
                                                    if calendar_reschedule_date_loop > job.scheduled_end_date:
                                                        
                                                        job.scheduled_end_date = calendar_reschedule_date_loop
                                                    else:
                                                        pass
                                                    break
                            
                            
                                            elif list(employees.values())[0] != 0 and affected_resources < list(employees.values())[0] and list(employees.values())[1].lower() == craft.lower():
                                            
                                                employees[list(employees.keys())[0]]= list(employees.values())[0] - affected_resources
                                                
                                                if calendar_reschedule_date_loop not in list(job.employees.keys()):
                                                    job.employees[calendar_reschedule_date_loop] = [{list(employees.keys())[0]: affected_resources}]
                                                
                                                else:
                                                    employee_exist_in_key = False
                                                    index = 0
                                                    for items in job.employees[calendar_reschedule_date_loop]:
                                                        if list(items.keys())[0] == list(employees.keys())[0]:
                                                            employee_exist_in_key = True
                                                            break
                                                        index +=1

                                                    if employee_exist_in_key == True:
                                                        current_employee_resource_allocated =list(job.employees[calendar_reschedule_date_loop][index].values())[0]
                                                        job.employees[calendar_reschedule_date_loop][index] = {list(employees.keys())[0]: current_employee_resource_allocated + affected_resources}
                                                    else:
                                                        job.employees[calendar_reschedule_date_loop].append({list(employees.keys())[0]: affected_resources})
                            
                            
                                                affected_resources = affected_resources- affected_resources #affected_resources = 0


                                                if affected_resources == 0:
                                                    if calendar_reschedule_date_loop > job.scheduled_end_date:
                                                        
                                                        job.scheduled_end_date = calendar_reschedule_date_loop
                                                    else:
                                                        pass
                                                    break
                        
                                            else:
                                                continue 
                                        calendar_reschedule_date_loop += dt.timedelta(days=1)
                                        if calendar_reschedule_date_loop > ed:
                                            unable_to_reschedule_hours += affected_resources
                                            affected_resources = 0

                                            if len(list_of_unable_to_reschedule_hours) == 0:
                                                
                                                list_of_unable_to_reschedule_hours.append({job.job_id : unable_to_reschedule_hours})
                                                job.scheduled_end_date = "Job cannot be completed"
                                            else:
                                                job_in_list = False
                                                index = 0
                                                for items in list_of_unable_to_reschedule_hours:
                                                    if list(items.keys())[0] == job.job_id:
                                                        list_of_unable_to_reschedule_hours[index] = {job.job_id : unable_to_reschedule_hours}
                                                        job.scheduled_end_date = "Job cannot be completed"
                                                        job_in_list = True
                                                        break
                                                    index +=1
                                                if job_in_list  == False:
                                                    list_of_unable_to_reschedule_hours.append({job.job_id : unable_to_reschedule_hours})
                                                    job.scheduled_end_date = "Job cannot be completed"
                                        #End of Rescheduling algorithm


                                i +=1
                list_of_affected_jobs = list(set(list_of_affected_jobs))
                list_of_affected_jobs_id = list(set(list_of_affected_jobs_id))
                print("\n** Employee {} has been successfully removed from database **\n".format(emp_id))
                
                print("These jobs (by Job ID) are affected by employee last day of work on {} and leaving on {}:""\n""{}\n".format(last_day.date(), out_of_company_date.date(), list_of_affected_jobs_id))
                
                i = 0
               
                while i < len(list_of_affected_jobs):
                    j = 0
                    job_exist_in_unable_to_schedule_list = False
                    while j < len(list_of_unable_to_reschedule_hours):
                        if list_of_affected_jobs[i].job_id == list(list_of_unable_to_reschedule_hours[j].keys())[0]:
                            del list_of_affected_jobs[i]
                            
                            job_exist_in_unable_to_schedule_list = True
                            break
                        else:
                            j +=1
                    if job_exist_in_unable_to_schedule_list == False:
                        i +=1
                    else:
                        pass

                for jobs in list_of_affected_jobs:    
                    
                    print("Job ID: {} with a deadline: {} ---> New Scheduled End Date {}""\n""".format( jobs.job_id ,jobs.due_date.date(), jobs.scheduled_end_date.date()))
                
                if len(list_of_unable_to_reschedule_hours) !=0:

                    print("Here is a list of job(s) (by Job ID) and their total affected hours that cannot be fully rescheduled (i.e Job cannot be completed) due to employee leaving: \n{}""\n""".format(list_of_unable_to_reschedule_hours))
            



        
                

