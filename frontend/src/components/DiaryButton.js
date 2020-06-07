import React, { Component } from "react";
class DiaryButton extends Component {
  initialState = {
    title: "",
  };

  state = this.initialState;
  handleChange = (event) => {
    const { title, value } = event.target;

    this.setState({
      [title]: value,
    });
  };
  submitForm = () => {
    if (this.state.title !== "") {
      this.props.handleSubmit(this.state);
      this.setState(this.initialState);
    }
  };
  render() {
    const { title } = this.state;

    return (
      <form>
        <div className="entry-grid">
          <label htmlFor="title">Title</label>
          <input
            size="10"
            type="text"
            title="title"
            id="title"
            value={title}
            onChange={this.handleChange}
          />
          <input type="button" value="+ Add Diary" onClick={this.submitForm} />
        </div>
      </form>
    );
  }
}

export default DiaryButton;
