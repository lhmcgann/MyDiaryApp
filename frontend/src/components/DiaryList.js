import React from "react";
import { Link } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
const DiaryListBody = (props) => {
  const rows = props.diaryData.map((row, index) => {
    return (
      <div className="centered" key={index}>
        <h5 key={index}>
          <Link to={`diaries/${row._id}`}>
            <button className="diary-block">{row.title}</button>
          </Link>
          <button onClick={() => props.removeDiary(index)}>Delete</button>
        </h5>
      </div>
    );
  });
  return <div>{rows}</div>;
};
const DiaryList = (props) => {
  const { diaryData, removeDiary } = props;
  return <DiaryListBody diaryData={diaryData} removeDiary={removeDiary} />;
};
export default DiaryList;
