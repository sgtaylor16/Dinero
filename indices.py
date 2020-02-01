import pandas as pd
import datetime
from dateutil.parser import parse




class market:
    def __init__(self):
        '''Init file establishes empty members'''
        self.table = pd.DataFrame(columns = ['Date','Close','Adj CLose','Pct Change'])

    def read_in(filepath):
        tempdata = pd.read_csv(filepath)
        tempdata2 = pd.DataFrame(columns =['Date','Close','Adj Close'])
        #match the data columns
        for col in tempdata.columns:
            if col.lower() == 'date'
                tempdata2['Date'] = tempdata[col]
            if col.lower() == 'close'
                tempdata2['Close'] = tempdata[col]
            if 'adj' in col.lower()
                    tempdata2['Adj Close'] = tempdata[col]
        #Check to make sure that data is continuoues if there is already data in the self table
        if len(self.table) > 0:
            if tempdata2['Date'].min() > self.table['Date']:
                raise KeyError:
                    print("New data does not overlap with current data")
        #Cut the new data off at the new date
        tempdata2
                



        
        



            

    def __update__(self):
        '''Private method to update attributes'''
        #Update date range
        mindate = self.table['Date'].min()
        maxdate = self.table['Date'].max()
        self.dates = [mindate,maxdate]
        #Calculate Pct Change
        self.table['Pct Change'] = self.table['Adj Close'].pct_change()*100


    def volatility(self,startdate = None,enddate = None):
        '''Calculates the standard deviation of daily returns between start date and enddate'''
        if startdate is None:
           startdate = self.table['Date'].min()
        if enddate is None:
            enddate = self.table['Date'].max()
        
        df = self.table

        if type(startdate) == str:
            startdate = parse(startdate)
        if type(enddate) == str:
            startdate = parse(startdate)
            
        df = df.loc[(df['Date'] >= startdate) & (df['Date'] <= enddate),:]
        startdate = self.table['Date'].min()
        enddate = self.table['Date'].max()


        data = df.loc[(df['Date'] >= startdate) & (df['Date'] <= enddate),'Pct Change']
        return data.std()

    def gains(self,startdate = None,enddate = None):
        df = self.table
        if startdate is None:
           startdate = self.table['Date'].min()
        if enddate is None:
            enddate = self.table['Date'].max()
        #Check to see if startdates are in data
        if startdate < df['Date'].min():
            raise ValueError('start date < table mindate')
        elif enddate> df['Date'].max():
            raise ValueError('enddate > table maxdate')
        else: #continue calculating
            df = df.loc[(df['Date'] >= startdate) & (df['Date'] <= enddate),:]
            startdate = df['Date'].min()
            enddate = df['Date'].max()
            return df.loc[df['Date'] == enddate,'Close'].iloc[0] / df.loc[df['Date'] == startdate,'Close'].iloc[0]
            

    def newread(self,df,headers = {'Close':'Close','Date':'DATE'}):
        '''File to read in table of data as a new index class
        Keyword Arguments:
        filepath: string - path to csv file
        headers: List of tuples where each pair is the name of the columns for close and date
        '''
        newdata = df

        #find the headernanames
        dateheader = headers['Date']
        closeheader = headers['Close']

        #Populate the date column
        self.table['Date'] = newdata[dateheader]
        #Populate the  closing price
        self.table['Close'] = newdata[closeheader]
        #Calculate the attributes
        self.__update__()

    def to_json(self,fileout):
        temp = self.table.to_json(fileout)

    def read_json(self,filein):
        temp = pd.read_json(filein)
        self.table['Date'] = temp['Date']
        self.table['Close'] = temp['Close']
        self.__update__()

    


        

