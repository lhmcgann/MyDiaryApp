import React, { Component } from "react";
import EntryList from "./EntryList";
import EntryButton from "./EntryButton";
import axios from "axios";
class DiaryHome extends Component {
  state = { title: "", entries: [] };
  componentDidMount() {
    axios
      .get("http://localhost:5000/diaries/" + this.props.match.params.d_id)
      .then((res) => {
        const diary = res.data; //.diaries;
        this.setState({ title: diary.title, entries: diary.entries });
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
      });
  }
  handleSubmit = (title) => {
    this.makePostCall(title).then((callResult) => {
      if (callResult !== false) {
        this.setState({ entries: [...this.state.entries, callResult] });
      }
    });
  };
  makePostCall(title) {
    return axios
      .post(
        "http://localhost:5000/diaries/" +
          this.props.match.params.d_id +
          "/entries",
        title
      )
      .then(function (response) {
        console.log(response);
        response.status = 201;
        return response.data;
      })
      .catch(function (error) {
        console.log(error);
        return false;
      });
  }
  makeDeleteCall(entry) {
    return axios
      .delete(
        "http://localhost:5000/diaries/" +
          this.props.match.params.d_id +
          "/entries/" +
          entry._id
      )
      .then(function (response) {
        console.log(response);
        return true;
      })
      .catch(function (error) {
        console.log(error);
        return false;
      });
  }
  removeEntry = (index) => {
    const { entries } = this.state;
    const entry = entries[index];
    this.makeDeleteCall(entry).then((callResult) => {
      if (callResult !== false) {
        this.setState({
          entries: entries.filter((entry, i) => {
            return i !== index;
          }),
        });
      }
    });
  };
  sortRecency(recency) {
    axios
      .get(
        "http://localhost:5000/diaries/" +
          this.props.match.params.d_id +
          "/entries",
        { params: { sortBy: recency } }
      )
      .then((res) => {
        const entries = res.data; //.diaries;
        this.setState({ entries: entries });
        return true;
      })
      .catch(function (error) {
        //Not handling the error. Just logging into the console.
        console.log(error);
        return true;
      });
  }
  render() {
    const title = this.state.title;
    const entries = this.state.entries;
    return (
      <div className="centered">
        <div className="dropdown">
          <button className="dropbtn">Sort By</button>
          <div className="dropdown-content">
            <div>
              <button onClick={() => this.sortRecency("mostRecent")}>
                Most Recent
              </button>
            </div>
            <div>
              <button onClick={() => this.sortRecency("leastRecent")}>
                Least Recent
              </button>
            </div>
          </div>
        </div>
        <h1>{title}</h1>
        <EntryButton handleSubmit={this.handleSubmit} />

        <EntryList entryData={entries} removeEntry={this.removeEntry} />
      </div>
    );
  }
}
export default DiaryHome;
