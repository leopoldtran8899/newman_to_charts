#!/usr/bin/env python

__author__ = 'Tien Tran'
import os, sys, time, thread
import plotly
import plotly.graph_objs as go


def read_postman_result(filename):
    print '\nReading files'
    test_result_list = []
    if os.path.exists(filename):
        with open(filename) as result_file:
            for line in result_file:
                if line.startswith('Folder') or line.startswith('Collection') or line.startswith('Total'):
                    line = line.replace('Folder', '')
                    results = [int(s) for s in line.split() if s.isdigit()]
                    column = filter(lambda c: c.isalpha(), line.rstrip())
                    n = [column, results]
                    test_result_list.append(n)
    return test_result_list


def create_stack_bar_chart(test_result_list, chart_name):
    print '\nCreating chart'
    trace1 = go.Bar(
        x=[i[0] for i in test_result_list],
        y=[i[1][0] for i in test_result_list],
        name='Pass'
    )
    trace2 = go.Bar(
        x=[i[0] for i in test_result_list],
        y=[i[1][1] for i in test_result_list],
        name='Fail'
    )
    data = [trace1, trace2]
    layout = go.Layout(
        title='Chemarome API testing result',
        barmode='stack'
    )
    fig = go.Figure(data=data, layout=layout)
    plotly.offline.plot(fig, filename=chart_name)


def create_pie_chart(test_result_list, folder_name, chart_name):
    print '\nCreating chart'
    y = []
    for result in test_result_list:
        if result[0].startswith(folder_name):
            y = result[1]
    fig = {
        'data': [{'labels': ['Pass', 'Fail'],
                  'values': y,
                  'type': 'pie'}],
        'layout': {'title': 'Testing result: ' + folder_name}
    }
    plotly.offline.plot(fig, filename=chart_name+'.html')


# create_pie_chart(read_postman_result('result-processed'), 'Total', 'InvoicePieChart.html')


def run_newman_test(collection, output, environment=''):
    print '\nRunning test collection'
    processed_output = output + '_processed'

    if os.path.exists(collection):
        if (environment != ''):
            command = 'newman -c ' + collection + ' -e ' + environment + ' -H ' + output + '.html -k > raw_result && cat raw_result | perl -pe \'s/\e([^\[\]]|\[.*?[a-zA-Z]|\].*?\\a)//g\' | col -b > ' + processed_output
        else:
            command = 'newman -c ' + collection + ' -H ' + output + '.html -k > raw_result && cat raw_result | perl -pe \'s/\e([^\[\]]|\[.*?[a-zA-Z]|\].*?\\a)//g\' | col -b > ' + processed_output

    os.system(command)
    return processed_output



def print_usage():
    print 'Usage: \n'


def progress_bar(finish):
    while finish:
        time.sleep(2)
        sys.stdout.write('.')
        sys.stdout.flush()


collection = ''
environment = ''
output_name = ''
folder = ''
finish = 1
if len(sys.argv) < 4:
    print_usage()
elif sys.argv[1] == 'pie':
    for i in range(2, len(sys.argv) - 1, 2):
        if sys.argv[i] == '-c':
            collection = sys.argv[i + 1]
            continue
        if sys.argv[i] == '-e':
            environment = sys.argv[i + 1]
            continue
        if sys.argv[i] == '-n':
            output_name = sys.argv[i + 1]
            continue
        if sys.argv[i] == '-f':
            folder = sys.argv[i + 1]
            continue
        else:
            print_usage()
            sys.exit('Undefined argument')

    thread.start_new(progress_bar, (finish,))
    processed_result = run_newman_test(collection, output_name, environment)
    create_pie_chart(read_postman_result(processed_result), folder, output_name)
    finish = 0
    print 'Finished.\n'

elif sys.argv[1] == 'bar':
    for i in range(2, len(sys.argv) - 1, 2):
        if sys.argv[i] == '-c':
            collection = sys.argv[i + 1]
            continue
        if sys.argv[i] == '-e':
            environment = sys.argv[i + 1]
            continue
        if sys.argv[i] == '-n':
            output_name = sys.argv[i + 1]
            continue
        if sys.argv[i] == '-f':
            folder = sys.argv[i + 1]
            continue
        else:
            print_usage()
            sys.exit('Undefined argument')
    thread.start_new(progress_bar, (finish,))
    processed_result = run_newman_test(collection, output_name, environment)
    create_stack_bar_chart(read_postman_result(processed_result), output_name)
    finish = 0
    print 'Finished.\n'

else:
    print_usage()
    sys.exit('Undefined argument')


# run_newman_test('Chemarome_5May.json', 'testOutput', 'Chemarome.postman_environment')
# test_name pie -c collection -e environment -n output_name -f folder_name
# test_name bar -c collection -e environment -n output_name -f folder_name
