import os

class TSVLogger:

    def __init__(self, fpath, fields):
        '''
        Opens a TSV file in which to log data.

        Parameters
        ----------
        fpath : str
            A valid filepath to write data to.
        fields : list of str
            Names of fields (columns) to be included in the log file.
        '''
        self._f = open(fpath, 'w')
        self._fields = fields
        self._f.write('\t'.join(self._fields))

    def write(self, **params):
        '''
        Adds data to the TSV file line-by-line.
        '''
        vals = dict()
        for field in self._fields:
            if field in params:
                vals[field] = params[field]
            else:
                vals[field] = 'n/a'
        boilerplate = '\n' + '\t'.join(['{%s}'%key for key in self._fields])
        line = boilerplate.format(**vals)
        self._f.write(line)

    def close(self):
        self._f.close()

    def __del__(self):
        self.close()
