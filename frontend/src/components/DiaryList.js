import React from "react";
import { Link } from "react-router-dom";
const DiaryListBody = (props) => {
  const rows = props.diaryData.map((row, index) => {
    return (
      <div className="centered">
        <h5 key={index}>
          <Link to={`diaries/${row._id}`}>
            <button class="diary-block">{row.title}</button>
          </Link>
          <button onClick={() => props.removeDiary(index)}>Delete</button>
        </h5>
      </div>
    );
  });
  return <tbody>{rows}</tbody>;
};
const DiaryList = (props) => {
  const { diaryData, removeDiary} = props;
  return (
    <table>
      <DiaryListBody diaryData={diaryData} removeDiary={removeDiary} />
    </table>
  );
};
export default DiaryList;
