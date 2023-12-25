# Databricks notebook source
import unittest2
import logging
class DataBricksTestCase(unittest2.TestCase):

    """Basic common test case for Spark. Provides a Spark context as sc.
    For non local mode testing you can either override sparkMaster
    or set the enviroment property SPARK_MASTER for non-local mode testing."""

    @classmethod
    def getMaster(cls):
        return cs.master

    def setUp(self):
        """Setup a basic Spark context for testing"""
        #self.sc = SparkContext(self.getMaster()) 
        self.sc = sc #Added by René Nadoerp
        self.logger = logging.getLogger('py4j')
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        """
        Tear down the basic panda spark test case. This stops the running
        context and does a hack to prevent Akka rebinding on the same port.
        """
        self.logger.setLevel(logging.ERROR)
        pass
        #self.sc.stop()
        # To avoid Akka rebinding to the same port, since it doesn't unbind
        # immediately on shutdown
        #self.sc._jvm.System.clearProperty("spark.driver.port")

    def assertRDDEquals(self, expected, result):
        return self.compareRDD(expected, result) == []

    def compareRDD(self, expected, result):
        expectedKeyed = expected.map(lambda x: (x, 1))\
                                .reduceByKey(lambda x, y: x + y)
        resultKeyed = result.map(lambda x: (x, 1))\
                            .reduceByKey(lambda x, y: x + y)
        return expectedKeyed.cogroup(resultKeyed)\
                            .map(lambda x: tuple(map(list, x[1])))\
                            .filter(lambda x: x[0] != x[1]).take(1)

    def assertRDDEqualsWithOrder(self, expected, result):
        return self.compareRDDWithOrder(expected, result) == []

    def compareRDDWithOrder(self, expected, result):
        def indexRDD(rdd):
            return rdd.zipWithIndex().map(lambda x: (x[1], x[0]))
        indexExpected = indexRDD(expected)
        indexResult = indexRDD(result)
        return indexExpected.cogroup(indexResult)\
                            .map(lambda x: tuple(map(list, x[1])))\
                            .filter(lambda x: x[0] != x[1]).take(1)

    def assertDataFrameEqual(self, expected, result, tol=0):
      """Assert that two DataFrames contain the same data.
      When comparing inexact fields uses tol.
      """

      self.assertEqual(expected.schema, result.schema)
      try:
          expectedRDD = expected.rdd.cache()
          resultRDD = result.rdd.cache()
          self.assertEqual(expectedRDD.count(), resultRDD.count())

          def zipWithIndex(rdd):
              """Zip with index (idx, data)"""
              return rdd.zipWithIndex().map(lambda x: (x[1], x[0]))

          def equal(x, y):
              if (len(x) != len(y)):
                  return False
              elif (x == y):
                  return True
              else:
                  for idx in range(len(x)):
                      a = x[idx]
                      b = y[idx]
                      if isinstance(a, float):
                          if (abs(a - b) > tol):
                              return False
                      else:
                          if a != b:
                              return False
              return True
          expectedIndexed = zipWithIndex(expectedRDD)
          resultIndexed = zipWithIndex(resultRDD)
          joinedRDD = expectedIndexed.join(resultIndexed)
          unequalRDD = joinedRDD.filter(
              lambda x: not equal(x[1][0], x[1][1]))
          differentRows = unequalRDD.take(10)
          self.assertEqual([], differentRows)
      finally:
          expectedRDD.unpersist()
          resultRDD.unpersist()

# COMMAND ----------

from datetime import datetime
from pyspark.sql import Row
from pyspark.sql.types import *

class SimpleSQLTest(DataBricksTestCase):
    """A simple test."""

    def test_empty_expected_equal(self):
        
       
        allTypes = self.sc.parallelize([])
        df = spark.createDataFrame(allTypes, StructType([]))
        
        self.assertDataFrameEqual(df,df)
        
    def test_simple_expected_equal(self):
        allTypes = self.sc.parallelize([Row(
            i=1, s="string", d=1.0, lng=1,
            b=True, list=[1, 2, 3], dict={"s": 0}, row=Row(a=1),
            time=datetime(2014, 8, 1, 14, 1, 5))])
        
        df = allTypes.toDF()
     
         
        self.assertDataFrameEqual(df, df)
        
    def test_simple_expected_equal_dept_emp(self):
    
        # Create the Departments
        department1 = Row(id='123456', name='Computer Science')
        department2 = Row(id='789012', name='Mechanical Engineering')
        department3 = Row(id='345678', name='Theater and Drama')
        department4 = Row(id='901234', name='Indoor Recreation')

        # Create the Employees
        Employee = Row("firstName", "lastName", "email", "salary")
        employee1 = Employee('michael', 'armbrust', 'no-reply@berkeley.edu', 100000)
        employee2 = Employee('xiangrui', 'meng', 'no-reply@stanford.edu', 120000)
        employee3 = Employee('matei', None, 'no-reply@waterloo.edu', 140000)
        employee4 = Employee(None, 'wendell', 'no-reply@berkeley.edu', 160000)

        # Create Department rows
        departments = [department1, department2]

        # Create the Department schema
        fields = [StructField('id', StringType(), nullable = True), StructField('name', StringType(), nullable=True)]
        schema = StructType(fields)

        df_result = spark.createDataFrame(departments, schema)
        df_expected = df_result

        self.assertDataFrameEqual(df_result, df_expected)
     
    def test_simple_expected_unequal_dept_emp(self):
    
        # Create the Departments
        department1 = Row(id='123456', name='Computer Science')
        department2 = Row(id='789012', name='Mechanical Engineering')
        department3 = Row(id='345678', name='Theater and Drama')
        department4 = Row(id='901234', name='Indoor Recreation')

        # Create the Employees
        Employee = Row("firstName", "lastName", "email", "salary")
        employee1 = Employee('michael', 'armbrust', 'no-reply@berkeley.edu', 100000)
        employee2 = Employee('xiangrui', 'meng', 'no-reply@stanford.edu', 120000)
        employee3 = Employee('matei', None, 'no-reply@waterloo.edu', 140000)
        employee4 = Employee(None, 'wendell', 'no-reply@berkeley.edu', 160000)

        # Create Department rows
        departmentsA = [department1, department2, department3]
        departmentsB = [department1, department3, department4]

        # Create the Department schema
        fields = [StructField('id', StringType(), nullable = True), StructField('name', StringType(), nullable=True)]
        schema = StructType(fields)
        
  
        df_result   = spark.createDataFrame(departmentsA, schema)
        df_expected = spark.createDataFrame(departmentsB, schema)

        self.assertDataFrameEqual(df_result, df_expected)

    def test_simple_close_equal(self):
        allTypes1 = self.sc.parallelize([Row(
            i=1, s="string", d=1.0, lng=1,
            b=True, list=[1, 2, 3], dict={"s": 0}, row=Row(a=1),
            time=datetime(2014, 8, 1, 14, 1, 5))])
        allTypes2 = self.sc.parallelize([Row(
            i=1, s="string", d=1.001, lng=1,
            b=True, list=[1, 2, 3], dict={"s": 0}, row=Row(a=1),
            time=datetime(2014, 8, 1, 14, 1, 5))])
        self.assertDataFrameEqual(allTypes1.toDF(), allTypes2.toDF(), 0.1)

    @unittest2.expectedFailure
    def test_simple_close_unequal(self):
        allTypes1 = self.sc.parallelize([Row(
            i=1, s="string", d=1.0, lng=1,
            b=True, list=[1, 2, 3], dict={"s": 0}, row=Row(a=1),
            time=datetime(2014, 8, 1, 14, 1, 5))])
        allTypes2 = self.sc.parallelize([Row(
            i=1, s="string", d=1.001, lng=1,
            b=True, list=[1, 2, 3], dict={"s": 0}, row=Row(a=1),
            time=datetime(2014, 8, 1, 14, 1, 5))])
        self.assertDataFrameEqual(allTypes1.toDF(), allTypes2.toDF(), 0.0001)

    @unittest2.expectedFailure
    def test_very_simple_close_unequal(self):
        allTypes1 = self.sc.parallelize([Row(d=1.0)])
        allTypes2 = self.sc.parallelize([Row(d=1.001)])
        self.assertDataFrameEqual(allTypes1.toDF(), allTypes2.toDF(), 0.0001)

    @unittest2.expectedFailure
    def test_dif_schemas_unequal(self):
        allTypes1 = self.sc.parallelize([Row(d=1.0)])
        allTypes2 = self.sc.parallelize([Row(d="1.0")])
        self.assertDataFrameEqual(allTypes1.toDF(), allTypes2.toDF(), 0.0001)

    @unittest2.expectedFailure
    def test_empty_dataframe_unequal(self):
        allTypes = self.sc.parallelize([Row(
            i=1, s="string", d=1.001, lng=1,
            b=True, list=[1, 2, 3], dict={"s": 0}, row=Row(a=1),
            time=datetime(2014, 8, 1, 14, 1, 5))])
        empty = self.sc.parallelize([])
        self.assertDataFrameEqual(
            allTypes.toDF(),
            self.sqlCtx.createDataFrame(empty, allTypes.toDF().schema), 0.1)

# COMMAND ----------

import sys
runner = unittest2.TextTestRunner(sys.stdout,verbosity=2)
result = runner.run(unittest2.makeSuite(SimpleSQLTest))


# COMMAND ----------

allTypes = sc.parallelize([])
df = spark.createDataFrame(allTypes, StructType([]))

# COMMAND ----------

df.toPandas()

# COMMAND ----------

  allTypes = sc.parallelize([Row(
            i=1, s="string", d=1.0, lng=1,
            b=True, list=[1, 2, 3], dict={"s": 0}, row=Row(a=1),
            time=datetime(2014, 8, 1, 14, 1, 5))])
        
  df = allTypes.toDF()
     

# COMMAND ----------

display(df)

# COMMAND ----------

df.toPandas()

# COMMAND ----------

# Create the Departments
department1 = Row(id='123456', name='Computer Science')
department2 = Row(id='789012', name='Mechanical Engineering')
department3 = Row(id='345678', name='Theater and Drama')
department4 = Row(id='901234', name='Indoor Recreation')

# Create the Employees
Employee = Row("firstName", "lastName", "email", "salary")
employee1 = Employee('michael', 'armbrust', 'no-reply@berkeley.edu', 100000)
employee2 = Employee('xiangrui', 'meng', 'no-reply@stanford.edu', 120000)
employee3 = Employee('matei', None, 'no-reply@waterloo.edu', 140000)
employee4 = Employee(None, 'wendell', 'no-reply@berkeley.edu', 160000)

# Create Department rows
departments = [department1, department2]

# Create the Department schema
fields = [StructField('id', StringType(), nullable = True), StructField('name', StringType(), nullable=True)]
schema = StructType(fields)

df_result = spark.createDataFrame(departments, schema)
df_expected = df_result

# COMMAND ----------

display(df_result)

# COMMAND ----------


