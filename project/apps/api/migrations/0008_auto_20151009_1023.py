# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20151009_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contest',
            name='level',
            field=models.IntegerField(default=1, choices=[(1, b'International'), (2, b'District'), (4, b'Prelims')]),
        ),
        migrations.AlterField(
            model_name='contest',
            name='year',
            field=models.IntegerField(default=2015, choices=[(2016, b'2016'), (2015, b'2015'), (2014, b'2014'), (2013, b'2013'), (2012, b'2012'), (2011, b'2011'), (2010, b'2010'), (2009, b'2009'), (2008, b'2008'), (2007, b'2007'), (2006, b'2006'), (2005, b'2005'), (2004, b'2004'), (2003, b'2003'), (2002, b'2002'), (2001, b'2001'), (2000, b'2000'), (1999, b'1999'), (1998, b'1998'), (1997, b'1997'), (1996, b'1996'), (1995, b'1995'), (1994, b'1994'), (1993, b'1993'), (1992, b'1992'), (1991, b'1991'), (1990, b'1990'), (1989, b'1989'), (1988, b'1988'), (1987, b'1987'), (1986, b'1986'), (1985, b'1985'), (1984, b'1984'), (1983, b'1983'), (1982, b'1982'), (1981, b'1981'), (1980, b'1980'), (1979, b'1979'), (1978, b'1978'), (1977, b'1977'), (1976, b'1976'), (1975, b'1975'), (1974, b'1974'), (1973, b'1973'), (1972, b'1972'), (1971, b'1971'), (1970, b'1970'), (1969, b'1969'), (1968, b'1968'), (1967, b'1967'), (1966, b'1966'), (1965, b'1965'), (1964, b'1964'), (1963, b'1963'), (1962, b'1962'), (1961, b'1961'), (1960, b'1960'), (1959, b'1959'), (1958, b'1958'), (1957, b'1957'), (1956, b'1956'), (1955, b'1955'), (1954, b'1954'), (1953, b'1953'), (1952, b'1952'), (1951, b'1951'), (1950, b'1950'), (1949, b'1949'), (1948, b'1948'), (1947, b'1947'), (1946, b'1946'), (1945, b'1945'), (1944, b'1944'), (1943, b'1943'), (1942, b'1942'), (1941, b'1941'), (1940, b'1940'), (1939, b'1939')]),
        ),
        migrations.AlterField(
            model_name='convention',
            name='year',
            field=models.IntegerField(default=2015, null=True, blank=True, choices=[(2016, b'2016'), (2015, b'2015'), (2014, b'2014'), (2013, b'2013'), (2012, b'2012'), (2011, b'2011'), (2010, b'2010'), (2009, b'2009'), (2008, b'2008'), (2007, b'2007'), (2006, b'2006'), (2005, b'2005'), (2004, b'2004'), (2003, b'2003'), (2002, b'2002'), (2001, b'2001'), (2000, b'2000'), (1999, b'1999'), (1998, b'1998'), (1997, b'1997'), (1996, b'1996'), (1995, b'1995'), (1994, b'1994'), (1993, b'1993'), (1992, b'1992'), (1991, b'1991'), (1990, b'1990'), (1989, b'1989'), (1988, b'1988'), (1987, b'1987'), (1986, b'1986'), (1985, b'1985'), (1984, b'1984'), (1983, b'1983'), (1982, b'1982'), (1981, b'1981'), (1980, b'1980'), (1979, b'1979'), (1978, b'1978'), (1977, b'1977'), (1976, b'1976'), (1975, b'1975'), (1974, b'1974'), (1973, b'1973'), (1972, b'1972'), (1971, b'1971'), (1970, b'1970'), (1969, b'1969'), (1968, b'1968'), (1967, b'1967'), (1966, b'1966'), (1965, b'1965'), (1964, b'1964'), (1963, b'1963'), (1962, b'1962'), (1961, b'1961'), (1960, b'1960'), (1959, b'1959'), (1958, b'1958'), (1957, b'1957'), (1956, b'1956'), (1955, b'1955'), (1954, b'1954'), (1953, b'1953'), (1952, b'1952'), (1951, b'1951'), (1950, b'1950'), (1949, b'1949'), (1948, b'1948'), (1947, b'1947'), (1946, b'1946'), (1945, b'1945'), (1944, b'1944'), (1943, b'1943'), (1942, b'1942'), (1941, b'1941'), (1940, b'1940'), (1939, b'1939')]),
        ),
    ]