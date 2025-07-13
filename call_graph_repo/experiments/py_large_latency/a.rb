require 'benchmark'
require 'json'
require 'net/http'
require 'date'

import_times = {}

import_times[:date] = Benchmark.realtime { require 'date' }
import_times[:json] = Benchmark.realtime { require 'json' }
import_times[:net_http] = Benchmark.realtime { require 'net/http' }

puts "Import Times:"
import_times.each do |package, time|
  puts "#{package}: #{time.round(4)} seconds"
end

today = Date.today
puts "Today is: #{today}"

sample_json = { name: "Alice", age: 30 }.to_json
puts "Sample JSON: #{sample_json}"

begin
  uri = URI('http://example.com')
  response = Net::HTTP.get(uri)
  puts "Response from example.com (first 100 characters): #{response[0..100]}..."
rescue SocketError => e
  puts "Error fetching URL: #{e.message}"
end