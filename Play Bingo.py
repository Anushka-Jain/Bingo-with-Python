import numpy as np
from random import shuffle, random, sample
from copy import deepcopy
import matplotlib.pyplot as plt
from fpdf import FPDF
from scipy.interpolate import make_interp_spline
from scipy import stats
from warnings import filterwarnings
import pandas as pd
from math import factorial
filterwarnings("ignore", category = DeprecationWarning)
filterwarnings("ignore", category = RuntimeWarning)

# Check for Integer Input from Game Menu
def value_input(prompt):
    value = input(prompt)
    if not value.isdigit():
        print("Invalid option! Please try again")
        return value_input(prompt)
    elif int(value) not in (1,2,3):
        print("Invalid option! Please try again")
        return value_input(prompt)
    else:
        return int(value)

# Check if Histogram is required
def check_histogram(prompt):
    value = input(prompt)
    if (value == 'Y' or value == 'y'or value == 'N' or value == 'n'):
        return value
    else:
        print("Invalid entry! Enter again!")
        return check_histogram(prompt)

# Check for Default Settings
def select_default(prompt, num_of_players):
    selected_size = input(prompt)
    if not selected_size.isdigit():
        print("Choose a valid default size value")
        return select_default(prompt,num_of_players)
    elif int(selected_size) not in (3,5,7,9):
        print("Invalid option! Please try again")
        return select_default(prompt,num_of_players)
    else:
        return create_default(int(selected_size),num_of_players)


def create_default(size,num_of_players):
    free_cells = 1
    if(size ==3):
        l_range, u_range = 1, 27
    elif(size == 5):
        l_range, u_range = 1, 75
    elif(size == 7):
        l_range, u_range = 1, 147
    elif(size == 9):
        l_range, u_range = 1, 243
    number_range = u_range - l_range + 1
    return size, l_range, u_range, free_cells, number_range


def check_number_as_integer(prompt):
    number = input(prompt)
    if not number.isdigit():
        print("Invalid entry! Enter integer number!")
        return check_number_as_integer(prompt)
    elif int(number) < 1:
        print("Invalid entry! Please try again!")
        return check_number_as_integer(prompt)
    return int(number)


def check_scorecard_size(prompt):
    scorecard = input(prompt)
    if not scorecard.isdigit():
        print("Invalid entry! Enter integer number!")
        return check_scorecard_size(prompt)
    elif int(scorecard) <3:
        print("Invalid entry! Minimum grid size possible is 3. Please try again!")
        return check_scorecard_size(prompt)
    elif int(scorecard)%2 == 0:
        #Only odd grid size is allowed.
        print("Invalid entry! Only odd grid size possible!")
        return check_scorecard_size(prompt)
    elif int(scorecard) >= 25:
        check1 = input("WARNING! Range is too huge for the grid size. Simulation may take time. Enter 'Y' to proceed or 'N' to enter again" + "\n")
        if (check1 == 'Y' or check1 == 'y'):
            return int(scorecard)
        elif (check1 == 'N' or check1 == 'n'):
             return check_scorecard_size(prompt)
        else:
            print("Invalid entry! Please try again!")
            return check_scorecard_size(prompt)
    else:
        return int(scorecard)

#For checking free cells limit
def check_free_cells(prompt, scorecard_size):
    free_cells = input(prompt)
    if not free_cells.isdigit():
        print("Invalid entry! Enter integer number!")
        return check_free_cells(prompt, scorecard_size)
    elif int(free_cells) > scorecard_size-2:
        print("Invalid entry! Too many free cells. Max free cells allowed are", scorecard_size - 2,". Please try again!")
        return check_free_cells(prompt, scorecard_size)
    return int(free_cells)

# Check for Infeasible combinations for user input range
def range_maker(scorecard_size, num_of_freecells, num_of_players):
    range_checker = False
    while (range_checker == False):
        lower_range = check_number_as_integer("Enter lower limit of the range: ")
        upper_range = check_number_as_integer("Enter upper limit of the range: ")
        number_range = upper_range - lower_range + 1
        if (num_of_players > (factorial(number_range//scorecard_size)*scorecard_size)):
            print("Incorrect range. Kindly enter a higher range to avoid duplicacy of bingo cards (tickets)")
        elif number_range <= (scorecard_size**2 - num_of_freecells):
            print("Invalid range! Range entered is too short. Please try again!")
        elif number_range > 1000 * (scorecard_size**2 - num_of_freecells):
            check1 = input("WARNING! Range is too huge for the grid size. Simulation may take time. Enter 'Y' to proceed or 'N' to enter again" + "\n")
            if (check1 == 'Y' or check1 == 'y'):
                range_checker = True
            elif (check1 == 'N' or check1 == 'n'):
                 range_checker = False
            else:
                print("Invalid entry! Please try again!")
        else:
            range_checker = True
    return lower_range, upper_range, number_range

# Exporting All Tickets to PDF
def pdf_export(Tickets_List, grid_size):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_font('Times', '', 12)
    pdf.set_left_margin(0)
    pdf.set_right_margin(0)
    for i in range(len(Tickets_List)):
        pdf.add_page()
        pdf.rect(x = 5, y = 5, w = 200, h = 287, style = 'D')
        pdf.rect(x = 6.5, y = 6.5, w = 197, h = 284, style = 'D')
        pdf.cell(210, 15, txt=("Ticket Number " + str(i+1) + '\n'), align='C', ln=1)
        for j in range(grid_size):
            pdf.cell(210, 5, txt=(np.array2string(Tickets_List[i][j,:]) + '\n'), align='C', ln=1)
    pdf.output("Bingo Tickets.pdf")
    print("\n PDF WITH TICKETS EXPORTED TO CURRENT DIRECTORY !\n")

#To check if tickets need to be exported in a pdf or not
def check_print_condition(prompt, Tickets_List, scorecard_size):
    print_condition = input(prompt)
    if (print_condition == 'Y' or print_condition == 'y'):
        pdf_export(Tickets_List, scorecard_size)
    elif ( print_condition == 'N' or print_condition == 'n'):
        return
    else:
        print("Invalid entry! Please try again!")
        return check_print_condition(prompt, Tickets_List, scorecard_size)


def Ticket_Generator(num_tickets, grid_size, lower_limit, upper_limit, free_cells):
    # Example : grid_size = 5 for a 5*5 Bingo Card
    num_range = upper_limit - lower_limit + 1
    if num_range == (grid_size**2 - free_cells):
        col_range = (num_range // grid_size) + 1
    else:
        col_range = num_range // grid_size
    list_ticket = []
    for i in range(num_tickets):
        # For each row of tickets, get gride_size unique numbers from the specified range and then transpose them.
        ticket = np.array([(sample(range(lower_limit + (i * col_range), lower_limit + ((i + 1) * col_range)), grid_size)) for i in range(grid_size)]).T
        if(free_cells == 1):
            # Free cell placement in centre for 1 free cell
            ticket[grid_size // 2, grid_size // 2] = 0
        else:
            # Free cell placement
            for i in range(free_cells):
                ticket[i,i+1] = 0
        list_ticket.append(ticket)
    return list_ticket;


def simulation_lists_generator(lower, upper, num_of_sim):
    output = list()
    for i in range(num_of_sim):
        row = list(range(lower, upper + 1))
        # Determining the order in which numbers are called in each simulation
        shuffle(row)
        output.append(row)
    return output


def bingo_checker(list_ticket, bingos):
    if(len(list_ticket) != 0):
        # Check the Ticket List in reverse order for Bingos
        for x in range(len(list_ticket)-1, -1, -1):
            ticket = list_ticket[x]
            row_sum = np.sum(ticket, axis = 1)
            col_sum = np.sum(ticket, axis = 0)
            row = ticket.shape[0] # Get number of rows from the ticket
            major_sum = sum(ticket[i][i] for i in range(row))
            minor_sum = sum(ticket[i][row - i - 1] for i in range(row))
            # A bingo in a card will have a row sum, column sum, or any diagonal sum of zero.
            if min(row_sum) == 0 or min(col_sum) == 0 or major_sum == 0 or minor_sum == 0 :
                bingos += 1
                del list_ticket[x]  # Delete ticket if bingo found
    return list_ticket, bingos


def number_cutter(list_ticket, sim_list, plot_bingos, scorecard_size, num_of_freecells, sim_counter):
    numbers_called = 0
    bingos = 0
    # Iterate over each number from the simulation_list
    for number in sim_list:
        if len(list_ticket) == 0:
            for i in range(numbers_called + 1, len(sim_list)):
                plot_bingos[sim_counter][i] += bingos
            break
        if numbers_called >= (scorecard_size - num_of_freecells):
            list_ticket, bingos = bingo_checker(list_ticket, bingos)
        if bingos != 0:
            plot_bingos[sim_counter][numbers_called + 1] += bingos
        numbers_called = numbers_called + 1
        for ticket in list_ticket:
            # Replacing number called with zero instead of a cross
            ticket[ticket == number] = 0

# Line PLots
def plotter(plot_bingos):
    #Max Winners
    x = np.array([x+1 for x in range(np.shape(plot_bingos)[1])]).flatten()
    y = np.amax(plot_bingos, axis = 0).flatten()
    X_Y_Spline = make_interp_spline(x, y)
    X_1 = np.linspace(x.min(), x.max(), 50)
    Y_1 = X_Y_Spline(X_1)

    #Min Winners
    x = np.array([x+1 for x in range(np.shape(plot_bingos)[1])]).flatten()
    y = np.amin(plot_bingos, axis = 0).flatten()
    X_Y_Spline = make_interp_spline(x, y)
    X_2 = np.linspace(x.min(), x.max(), 50)
    Y_2 = X_Y_Spline(X_2)

    #plotting average winners
    x = np.array([x+1 for x in range(np.shape(plot_bingos)[1])]).flatten()
    y = np.sum(plot_bingos, axis = 0).flatten()
    y = y/(np.shape(plot_bingos)[0])  #find average
    X_Y_Spline = make_interp_spline(x, y)
    X_3 = np.linspace(x.min(), x.max(), 500)
    Y_3 = X_Y_Spline(X_3)

    #Standard Deviation
    x1 = np.array([x+1 for x in range(np.shape(plot_bingos)[1])]).flatten()
    yx = np.std(plot_bingos, axis = 0).flatten()
    y = np.sum(plot_bingos, axis = 0).flatten()
    y = y/(np.shape(plot_bingos)[0])  #find average
    y1 = np.array([y[x] + yx[x] for x in range(np.shape(plot_bingos)[1])])    #avg + sd
    X_Y_Spline = make_interp_spline(x1, y1)
    X_4 = np.linspace(x1.min(), x1.max(), 500)
    Y_4 = X_Y_Spline(X_3)

    x2 = np.array([x+1 for x in range(np.shape(plot_bingos)[1])]).flatten()
    y2 = np.array([y[x] - yx[x] for x in range(np.shape(plot_bingos)[1])])    #avg-sd
    X_Y_Spline = make_interp_spline(x2, y2)
    X_5 = np.linspace(x2.min(), x2.max(), 500)
    Y_5 = X_Y_Spline(X_4)

    #Plotting everything
    plt.plot(X_1, Y_1, color="blue", linestyle='dashed')    #Max
    plt.plot(X_2, Y_2, color="blue", linestyle='dashed')    #Min
    plt.plot(X_3, Y_3, 'b')                                 #Average
    plt.fill_between(X_4, Y_4, Y_5, color='blue', alpha=.2) #Standard Deviation
    plt.title('Number of winners per numbers called')
    plt.xlabel('Total numbers called')
    plt.ylabel('Winners')
    plt.show()


def descriptive_extension(plot_bingos, num_of_simulations, number_range):
    mean = np.mean(plot_bingos, axis = 0, dtype=None)         #Mean
    median = np.median(plot_bingos, axis = 0)                 #Median
    percentile1 = np.percentile(plot_bingos, 25, axis=0, interpolation='lower')    #Percentiles
    percentile3 = np.percentile(plot_bingos, 75, axis=0, interpolation='lower')    #Percentiles
    skew = stats.skew(plot_bingos, axis=0)                    #Skewness
    kurt = stats.kurtosis(plot_bingos, axis=0, fisher=True)   #Excessive Kurtosis
    range1 = [ x for x in range(1, number_range+1) ]
    data = {'Numbers Called':range1, 'Mean':mean, 'Median':median, 'Quartile 1':percentile1, 'Quartile 3':percentile3, 'Skewness':skew, 'Kurtosis':kurt}
    df = pd.DataFrame(data)
    df.to_csv("Descriptive_Statistics.csv", index = False, header = True)
    print("\n EXCEL WITH DESCRPTIVE STATISTICS EXPORTED TO CURRENT DIRECTORY !\n")


def histogram_extension(plot_bingos):
    hist = check_histogram("Do you want to plot histogram? Enter Y or N : ")
    if(hist == 'Y' or hist == 'y'):
        check = False
        while(check == False):
            x_hist = check_number_as_integer("Enter value of x to generate histogram: ")
            if (x_hist > np.shape(plot_bingos)[1]):
                print("Number entered is greater than the range. Please try again!\n")
            else:
                check= True
                vals = [i for i in range (1, x_hist + 1)]
                freq = list(np.sum(plot_bingos, axis = 0).flatten())  # col sum...
                copy_list = []
                copy_list.append(int(freq[0]))
                for i in range(1,x_hist):
                    copy_list.append(int(freq[i] - freq[i-1]))  #Getting unique bingos at each number called
                data = []
                for f, v in zip(copy_list, vals):
                    a = [v] * f                                 #Creating file for histogram (Frequency)
                    data.extend(a)

                if (len(data) == 0 or data[0]==x_hist):
                    print("\n", " "*10, "There were no bingos when", x_hist,"numbers were called!\n")
                    histogram_extension(plot_bingos)
                else:
                    plt.hist(x=data, bins = list(range(data[0], x_hist + 1)))
                    plt.xlabel('Numbers called')
                    plt.ylabel('Frequency of Bingos')
                    plt.title("Histogram")
                    plt.style.use('ggplot')
                    plt.show()
    elif (hist == 'N' or hist == 'n'):
        return
    else:
        print("Invalid entry! Please try again!\n")
        histogram_extension(plot_bingos)


def Game_checker():
    num_of_players = check_number_as_integer("\nEnter the number of players: ")
    num_of_simulations = check_number_as_integer("Enter simulations: ")
    if (num_of_players*num_of_simulations) > 15000:
        check1=input("\n WARNING! Entered game is too long! \n Are you sure you want to run such a game? Enter Y to confirm or N to re-enter : ")
        if (check1 == 'Y' or check1 == 'y'):
            a = 1 # dummy
        elif (check1 == 'N' or check1 == 'n'):
            num_of_players, num_of_simulations = Game_checker( )
        else:
            print("Invalid entry! Please try again!")
            num_of_players, num_of_simulations = Game_checker( )
    return num_of_players, num_of_simulations


def print_menu():
        print("\n"   + "*" * 37 + " WELCOME TO THE GAME OF BINGO "+ "*" * 37 + "\n")                    # Print Game Menu
        print("\t"*2 + "Welcome to the Bingo game"  + "\t" * 2 + " " * 33 + "|  B I N G O |" )
        print("\t"*2 + "What would you like to do?" + "\t" * 2 + " " * 33 + "|  I         |")
        print("\t"*4 + " " * 57 + "|  N         |")
        print("\t"*4 + "1. Play with default setting"+ " " * 29 + "|  G         |")
        print("\t"*4 + " " * 57 + "|  O         |")
        print("\t"*4 + "2. Customise your inputs\n")
        print("\t"*4 + "3. Quit :(\n")
        print("*" *104)


def main():

    print_menu()
    option = value_input("Choose option : ")
    if(option == 3):
         # Exit out of the Game
        raise SystemExit
    else:
        num_of_players, num_of_simulations = Game_checker()
        if(option == 1):
            # For Default Options : Extension 2.1
            scorecard_size, lower_range, upper_range, num_of_freecells, number_range = select_default("Select default grid size : 3,5,7,9 : ", num_of_players)
        elif(option == 2):
            # For User Defined Inputs : Extension 2.1
            scorecard_size = check_scorecard_size("Enter grid size: ")
            num_of_freecells = check_free_cells("Enter free cells: ", scorecard_size)
            lower_range, upper_range, number_range = range_maker(scorecard_size, num_of_freecells, num_of_players)

    # Generate list of tickets/cards
    Tickets_List = Ticket_Generator(num_of_players, scorecard_size, lower_range, upper_range, num_of_freecells)

    # Generate a PDF file with all the Cards :  Extension 2.2
    check_print_condition("Do you want the tickets to be exported to a pdf? Enter Y or N :" + " ", Tickets_List, scorecard_size)
    print("\n" + " "*10 + " SIMULATION IN PROGRESS ... " + " "*10 + "\n")

    # Create a list of order of Numbers called for all Simulations
    simulation_list = simulation_lists_generator(lower_range, upper_range, num_of_simulations)

    # Create a 2D np Array to store the cumulative sum of bingos at each number call for all simulations.
    plot_bingos = np.zeros((num_of_simulations,number_range))

    sim_counter = 0

    # Iterate over each simulation
    for listn in simulation_list:
        Ticketcopy = deepcopy(Tickets_List)
        # For each ticket, number drawn from the simulation list is crossed
        number_cutter(Ticketcopy, listn, plot_bingos, scorecard_size, num_of_freecells, sim_counter)
        sim_counter += 1

    print("\n" + "*"*10 + " SIMULATION COMPLETE ! " + "*"*10 + "\n")

    # Plotting Line Plot
    plotter(plot_bingos)

    # Extension 1.1
    descriptive_extension(plot_bingos, num_of_simulations, number_range)

    # Extension 1.2
    histogram_extension(plot_bingos)


if __name__ == "__main__":
    main()
