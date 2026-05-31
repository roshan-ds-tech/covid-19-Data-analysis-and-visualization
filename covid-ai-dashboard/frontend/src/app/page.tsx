'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { ssr: false, loading: () => <div className="h-64 flex items-center justify-center text-gray-400">Loading Chart...</div> });

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [allCountries, setAllCountries] = useState<string[]>([]);
  const [selectedCountries, setSelectedCountries] = useState<string[]>(['US', 'India', 'Brazil', 'United Kingdom', 'France']);
  const [minDate, setMinDate] = useState('2020-01-22');
  const [maxDate, setMaxDate] = useState('2023-03-09');
  const [startDate, setStartDate] = useState('2020-01-22');
  const [endDate, setEndDate] = useState('2023-03-09');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInit = async () => {
      try {
        const [cRes, dRes] = await Promise.all([
          axios.get('http://localhost:8000/api/countries'),
          axios.get('http://localhost:8000/api/dates')
        ]);
        setAllCountries(cRes.data.countries);
        setMinDate(dRes.data.min_date);
        setMaxDate(dRes.data.max_date);
        setStartDate(dRes.data.min_date);
        setEndDate(dRes.data.max_date);
      } catch (err) {
        console.error("Init Error", err);
      }
    };
    fetchInit();
  }, []);

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const res = await axios.post('http://localhost:8000/api/dashboard', {
          countries: selectedCountries,
          start_date: startDate,
          end_date: endDate
        });
        setData(res.data);
      } catch (err) {
        console.error("Dashboard Error", err);
      } finally {
        setLoading(false);
      }
    };
    if (selectedCountries.length > 0) {
      fetchDashboard();
    }
  }, [selectedCountries, startDate, endDate]);

  const handleCountryToggle = (country: string) => {
    if (selectedCountries.includes(country)) {
      setSelectedCountries(selectedCountries.filter(c => c !== country));
    } else {
      setSelectedCountries([...selectedCountries, country]);
    }
  };

  const lineTraces = data?.trends ? Object.keys(data.trends).map(country => ({
    x: data.trends[country].dates,
    y: data.trends[country].cases,
    mode: 'lines',
    name: country
  })) : [];

  const barTrace = data?.top_affected ? [{
    x: data.top_affected.countries,
    y: data.top_affected.cases,
    type: 'bar',
    marker: { color: '#3b82f6' }
  }] : [];

  const mapTrace = data?.map ? [{
    type: 'choropleth',
    locationmode: 'country names',
    locations: data.map.countries,
    z: data.map.cases,
    colorscale: 'Blues',
    autocolorscale: false
  }] : [];

  const pieTrace = data?.kpi ? [{
    values: [data.kpi.total_cases, data.kpi.total_deaths],
    labels: ['Total Cases', 'Total Deaths'],
    type: 'pie',
    marker: { colors: ['#3b82f6', '#ef4444'] }
  }] : [];

  const scatterTrace = data?.scatter ? [{
    x: data.scatter.cases,
    y: data.scatter.deaths,
    mode: 'markers',
    type: 'scatter',
    text: data.scatter.countries,
    marker: { size: 12, color: '#8b5cf6', opacity: 0.7 }
  }] : [];

  const heatmapTrace = data?.heatmap ? [{
    z: data.heatmap.z,
    x: data.heatmap.x,
    y: data.heatmap.y,
    type: 'heatmap',
    colorscale: 'RdBu'
  }] : [];

  const predData = data?.prediction;
  const predTraces = predData ? [
    {
      x: predData.hist_dates,
      y: predData.hist_trend,
      mode: 'lines',
      name: 'Historical Trend',
      line: { dash: 'dash', color: '#6b7280' }
    },
    {
      x: predData.future_dates,
      y: predData.predicted_cases,
      mode: 'lines',
      name: '30-Day Forecast',
      line: { color: '#ef4444', width: 3 }
    }
  ] : [];

  const getCommonLayout = () => ({
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    font: { family: 'Inter, sans-serif', color: '#374151' },
    margin: { t: 40, r: 20, l: 40, b: 40 },
    xaxis: { gridcolor: '#f3f4f6' },
    yaxis: { gridcolor: '#f3f4f6' },
    autosize: true
  });

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <header className="bg-white border-b border-gray-200 px-8 py-4 shadow-sm flex items-center justify-between sticky top-0 z-50">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <span className="text-blue-600">COVID-19</span> Analytics
          </h1>
          <p className="text-sm text-gray-500">Enterprise Data Intelligence Platform</p>
        </div>
        {loading && <span className="text-sm font-medium text-blue-500 animate-pulse bg-blue-50 px-3 py-1 rounded-full">Refreshing Data...</span>}
      </header>

      <div className="flex">
        <aside className="w-80 bg-white border-r border-gray-200 p-6 h-[calc(100vh-73px)] sticky top-[73px] overflow-y-auto hidden md:block">
          <h2 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4">Filters & Controls</h2>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <div className="flex gap-2 mb-2">
              <input type="date" value={startDate} min={minDate} max={endDate} onChange={e => setStartDate(e.target.value)} className="w-full text-sm border-gray-300 border rounded p-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
            <div className="flex gap-2">
              <input type="date" value={endDate} min={startDate} max={maxDate} onChange={e => setEndDate(e.target.value)} className="w-full text-sm border-gray-300 border rounded p-2 focus:ring-blue-500 focus:border-blue-500" />
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Countries ({selectedCountries.length})
            </label>
            <div className="border border-gray-200 rounded-md max-h-64 overflow-y-auto p-2 bg-gray-50">
              {allCountries.map(c => (
                <label key={c} className="flex items-center space-x-2 p-1 hover:bg-white rounded cursor-pointer">
                  <input type="checkbox" checked={selectedCountries.includes(c)} onChange={() => handleCountryToggle(c)} className="rounded text-blue-600 focus:ring-blue-500" />
                  <span className="text-sm text-gray-700">{c}</span>
                </label>
              ))}
            </div>
          </div>
        </aside>

        <main className="flex-1 p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <h3 className="text-sm font-semibold text-gray-500 uppercase">Filtered Total Cases</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">{data?.kpi?.total_cases.toLocaleString() || '-'}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <h3 className="text-sm font-semibold text-gray-500 uppercase">Filtered Total Deaths</h3>
              <p className="text-3xl font-bold text-gray-900 mt-2">{data?.kpi?.total_deaths.toLocaleString() || '-'}</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm bg-gradient-to-br from-blue-50 to-indigo-50">
              <h3 className="text-sm font-semibold text-blue-600 uppercase">Latest Data Date</h3>
              <p className="text-3xl font-bold text-blue-900 mt-2">{data?.kpi?.latest_date || '-'}</p>
            </div>
          </div>

          {!data || data.error ? (
            <div className="bg-white p-8 rounded-xl border border-gray-200 text-center text-gray-500">
              {data?.error || "Waiting for data..."}
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Daily Cases Trend</h3>
                  <div className="w-full h-[300px]">
                    <Plot divId="line-chart" data={lineTraces as any} layout={{...getCommonLayout()}} config={{ responsive: true }} style={{width: '100%', height: '100%'}} />
                  </div>
                </div>
                
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Top Affected Countries</h3>
                  <div className="w-full h-[300px]">
                    <Plot divId="bar-chart" data={barTrace as any} layout={{...getCommonLayout()}} config={{ responsive: true }} style={{width: '100%', height: '100%'}} />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Global Spread (Map)</h3>
                  <div className="w-full h-[350px]">
                    <Plot divId="map-chart" data={mapTrace as any} layout={{...getCommonLayout(), margin: {t:0,b:0,l:0,r:0}, geo: {projection: {type: 'natural earth'}}}} config={{ responsive: true }} style={{width: '100%', height: '100%'}} />
                  </div>
                </div>
                
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Correlation Heatmap</h3>
                  <div className="w-full h-[350px]">
                    <Plot divId="heatmap-chart" data={heatmapTrace as any} layout={{...getCommonLayout()}} config={{ responsive: true }} style={{width: '100%', height: '100%'}} />
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Cases vs Deaths</h3>
                  <div className="w-full h-[250px]">
                    <Plot divId="pie-chart" data={pieTrace as any} layout={{...getCommonLayout(), showlegend: false}} config={{ responsive: true }} style={{width: '100%', height: '100%'}} />
                  </div>
                </div>
                
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Mortality Scatter</h3>
                  <div className="w-full h-[250px]">
                    <Plot divId="scatter-chart" data={scatterTrace as any} layout={{...getCommonLayout(), xaxis: {title: {text: 'Cases'}}, yaxis: {title: {text: 'Deaths'}}}} config={{ responsive: true }} style={{width: '100%', height: '100%'}} />
                  </div>
                </div>

                <div className="bg-white p-4 rounded-xl border border-blue-200 shadow-sm bg-gradient-to-b from-white to-blue-50">
                  <h3 className="text-lg font-semibold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="bg-blue-100 text-blue-600 p-1 rounded">🤖</span> AI Forecast: {predData?.country}
                  </h3>
                  {predData ? (
                    <div className="w-full h-[250px]">
                      <Plot divId="pred-chart" data={predTraces as any} layout={{...getCommonLayout(), showlegend: false}} config={{ responsive: true }} style={{width: '100%', height: '100%'}} />
                    </div>
                  ) : (
                    <p className="text-gray-500 text-sm mt-10 text-center">Select at least one country with sufficient data to view forecast.</p>
                  )}
                </div>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
