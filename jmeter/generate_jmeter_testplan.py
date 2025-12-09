#!/usr/bin/env python3
"""
Generate JMeter Test Plan XML for Kayak Performance Testing
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_jmeter_testplan():
    """Create comprehensive JMeter test plan"""
    
    # Root element
    jmeterTestPlan = ET.Element('jmeterTestPlan', {
        'version': '1.2',
        'properties': '5.0',
        'jmeter': '5.6.3'
    })
    
    # Hash Tree
    hashTree = ET.SubElement(jmeterTestPlan, 'hashTree')
    
    # Test Plan
    testPlan = ET.SubElement(hashTree, 'TestPlan', {
        'guiclass': 'TestPlanGui',
        'testclass': 'TestPlan',
        'testname': 'Kayak Performance Test',
        'enabled': 'true'
    })
    
    ET.SubElement(testPlan, 'stringProp', {'name': 'TestPlan.comments'}).text = 'Kayak Performance Test - 100 Concurrent Users'
    ET.SubElement(testPlan, 'boolProp', {'name': 'TestPlan.functional_mode'}).text = 'false'
    ET.SubElement(testPlan, 'boolProp', {'name': 'TestPlan.serialize_threadgroups'}).text = 'false'
    
    # Test Plan Hash Tree
    testPlanHashTree = ET.SubElement(hashTree, 'hashTree')
    
    # Thread Group
    threadGroup = ET.SubElement(testPlanHashTree, 'ThreadGroup', {
        'guiclass': 'ThreadGroupGui',
        'testclass': 'ThreadGroup',
        'testname': 'Kayak Users',
        'enabled': 'true'
    })
    
    ET.SubElement(threadGroup, 'stringProp', {'name': 'ThreadGroup.on_sample_error'}).text = 'continue'
    
    elementProp = ET.SubElement(threadGroup, 'elementProp', {
        'name': 'ThreadGroup.main_controller',
        'elementType': 'LoopController',
        'guiclass': 'LoopControlPanel',
        'testclass': 'LoopController',
        'testname': 'Loop Controller',
        'enabled': 'true'
    })
    ET.SubElement(elementProp, 'boolProp', {'name': 'LoopController.continue_forever'}).text = 'false'
    ET.SubElement(elementProp, 'stringProp', {'name': 'LoopController.loops'}).text = '-1'
    
    ET.SubElement(threadGroup, 'stringProp', {'name': 'ThreadGroup.num_threads'}).text = '100'
    ET.SubElement(threadGroup, 'stringProp', {'name': 'ThreadGroup.ramp_time'}).text = '30'
    ET.SubElement(threadGroup, 'boolProp', {'name': 'ThreadGroup.scheduler'}).text = 'true'
    ET.SubElement(threadGroup, 'stringProp', {'name': 'ThreadGroup.duration'}).text = '300'
    ET.SubElement(threadGroup, 'stringProp', {'name': 'ThreadGroup.delay'}).text = '0'
    
    # Thread Group Hash Tree
    threadHashTree = ET.SubElement(testPlanHashTree, 'hashTree')
    
    # HTTP Request Defaults
    configTestElement = ET.SubElement(threadHashTree, 'ConfigTestElement', {
        'guiclass': 'HttpDefaultsGui',
        'testclass': 'ConfigTestElement',
        'testname': 'HTTP Request Defaults',
        'enabled': 'true'
    })
    
    ET.SubElement(configTestElement, 'stringProp', {'name': 'HTTPSampler.domain'}).text = 'localhost'
    ET.SubElement(configTestElement, 'stringProp', {'name': 'HTTPSampler.port'}).text = '3000'
    ET.SubElement(configTestElement, 'stringProp', {'name': 'HTTPSampler.protocol'}).text = 'http'
    ET.SubElement(configTestElement, 'stringProp', {'name': 'HTTPSampler.contentEncoding'}).text = 'UTF-8'
    
    configHashTree = ET.SubElement(threadHashTree, 'hashTree')
    
    # CSV Data Set for test data
    csvDataSet = ET.SubElement(threadHashTree, 'CSVDataSet', {
        'guiclass': 'TestBeanGUI',
        'testclass': 'CSVDataSet',
        'testname': 'Test Data',
        'enabled': 'true'
    })
    ET.SubElement(csvDataSet, 'stringProp', {'name': 'filename'}).text = 'test_data/user_credentials.csv'
    ET.SubElement(csvDataSet, 'stringProp', {'name': 'fileEncoding'}).text = 'UTF-8'
    ET.SubElement(csvDataSet, 'stringProp', {'name': 'variableNames'}).text = 'user_email,user_password'
    ET.SubElement(csvDataSet, 'boolProp', {'name': 'recycle'}).text = 'true'
    ET.SubElement(csvDataSet, 'boolProp', {'name': 'stopThread'}).text = 'false'
    ET.SubElement(csvDataSet, 'stringProp', {'name': 'shareMode'}).text = 'shareMode.all'
    
    ET.SubElement(threadHashTree, 'hashTree')
    
    # Add HTTP Requests
    add_http_sampler(threadHashTree, 'Search Flights', 'GET', '/api/flights/search?page=1&page_size=20')
    add_http_sampler(threadHashTree, 'Search Hotels', 'GET', '/api/hotels/search?city=Los Angeles&page=1')
    add_http_sampler(threadHashTree, 'Search Cars', 'GET', '/api/cars/search?page=1&page_size=20')
    add_http_sampler(threadHashTree, 'User Login', 'POST', '/api/users/auth/login', 
                    '{"email":"${user_email}","password":"${user_password}"}')
    add_http_sampler(threadHashTree, 'Get User Profile', 'GET', '/api/users/888-44-3333')
    add_http_sampler(threadHashTree, 'Admin Dashboard', 'GET', '/api/admin/dashboard/stats')
    
    # Add Listeners
    add_summary_report(threadHashTree)
    add_aggregate_report(threadHashTree)
    add_view_results_tree(threadHashTree)
    
    # Prettify and return
    return prettify(jmeterTestPlan)

def add_http_sampler(parent, name, method, path, body=None):
    """Add HTTP Request sampler"""
    sampler = ET.SubElement(parent, 'HTTPSamplerProxy', {
        'guiclass': 'HttpTestSampleGui',
        'testclass': 'HTTPSamplerProxy',
        'testname': name,
        'enabled': 'true'
    })
    
    ET.SubElement(sampler, 'boolProp', {'name': 'HTTPSampler.postBodyRaw'}).text = 'true' if body else 'false'
    ET.SubElement(sampler, 'elementProp', {
        'name': 'HTTPsampler.Arguments',
        'elementType': 'Arguments',
        'guiclass': 'HTTPArgumentsPanel',
        'testclass': 'Arguments',
        'enabled': 'true'
    })
    
    if body:
        arguments = sampler.find('.//elementProp[@name="HTTPsampler.Arguments"]')
        collectionProp = ET.SubElement(arguments, 'collectionProp', {'name': 'Arguments.arguments'})
        elementProp = ET.SubElement(collectionProp, 'elementProp', {
            'name': '',
            'elementType': 'HTTPArgument'
        })
        ET.SubElement(elementProp, 'boolProp', {'name': 'HTTPArgument.always_encode'}).text = 'false'
        ET.SubElement(elementProp, 'stringProp', {'name': 'Argument.value'}).text = body
        ET.SubElement(elementProp, 'stringProp', {'name': 'Argument.metadata'}).text = '='
    
    ET.SubElement(sampler, 'stringProp', {'name': 'HTTPSampler.domain'})
    ET.SubElement(sampler, 'stringProp', {'name': 'HTTPSampler.port'})
    ET.SubElement(sampler, 'stringProp', {'name': 'HTTPSampler.protocol'})
    ET.SubElement(sampler, 'stringProp', {'name': 'HTTPSampler.path'}).text = path
    ET.SubElement(sampler, 'stringProp', {'name': 'HTTPSampler.method'}).text = method
    ET.SubElement(sampler, 'boolProp', {'name': 'HTTPSampler.follow_redirects'}).text = 'true'
    ET.SubElement(sampler, 'boolProp', {'name': 'HTTPSampler.auto_redirects'}).text = 'false'
    ET.SubElement(sampler, 'boolProp', {'name': 'HTTPSampler.use_keepalive'}).text = 'true'
    
    if body:
        headerManager = ET.SubElement(sampler, 'HeaderManager', {
            'guiclass': 'HeaderPanel',
            'testclass': 'HeaderManager',
            'testname': 'HTTP Header Manager',
            'enabled': 'true'
        })
        collectionProp = ET.SubElement(headerManager, 'collectionProp', {'name': 'HeaderManager.headers'})
        elementProp = ET.SubElement(collectionProp, 'elementProp', {'name': '', 'elementType': 'Header'})
        ET.SubElement(elementProp, 'stringProp', {'name': 'Header.name'}).text = 'Content-Type'
        ET.SubElement(elementProp, 'stringProp', {'name': 'Header.value'}).text = 'application/json'
    
    ET.SubElement(parent, 'hashTree')

def add_summary_report(parent):
    """Add Summary Report listener"""
    listener = ET.SubElement(parent, 'SummaryReport', {
        'guiclass': 'SummaryReport',
        'testclass': 'SummaryReport',
        'testname': 'Summary Report',
        'enabled': 'true'
    })
    ET.SubElement(parent, 'hashTree')

def add_aggregate_report(parent):
    """Add Aggregate Report listener"""
    listener = ET.SubElement(parent, 'ResultCollector', {
        'guiclass': 'StatVisualizer',
        'testclass': 'ResultCollector',
        'testname': 'Aggregate Report',
        'enabled': 'true'
    })
    ET.SubElement(listener, 'boolProp', {'name': 'ResultCollector.error_logging'}).text = 'false'
    ET.SubElement(parent, 'hashTree')

def add_view_results_tree(parent):
    """Add View Results Tree listener"""
    listener = ET.SubElement(parent, 'ResultCollector', {
        'guiclass': 'ViewResultsFullVisualizer',
        'testclass': 'ResultCollector',
        'testname': 'View Results Tree',
        'enabled': 'true'
    })
    ET.SubElement(listener, 'boolProp', {'name': 'ResultCollector.error_logging'}).text = 'false'
    ET.SubElement(parent, 'hashTree')

def prettify(elem):
    """Return a pretty-printed XML string"""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def main():
    """Generate and save JMeter test plan"""
    print("Generating JMeter test plan...")
    
    xml_content = create_jmeter_testplan()
    
    with open('kayak_performance_test.jmx', 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    print("✅ Test plan generated: kayak_performance_test.jmx")
    print()
    print("You can now run:")
    print("  jmeter -n -t kayak_performance_test.jmx -l results.jtl -e -o report/")

if __name__ == "__main__":
    main()
